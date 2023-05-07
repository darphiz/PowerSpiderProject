import logging
from contextlib import suppress
from celery import shared_task
from ngo_scraper.notification import Notify
from .services import PledgeListCrawler, PledgeScraper
from .models import PledgeIndexedUrl, CrawlCursor, NGO, Cause
from django.db import transaction
from django.utils.timezone import now
from django.conf import settings
from django.db.utils import IntegrityError
import re 

def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)


@shared_task(name="do_url_indexing")
def do_url_indexing(start, end):
    try:
        cause = Cause.objects.first().cause
        spider = PledgeListCrawler(start=start, end=end, cause=cause)
        links = spider.crawl_all()
    except Exception as e:
        Notify(settings.PLEDGE_HOOK).alert(Notify.error(f"Error crawling from {start} to {end}: {str(e)}"))
        return
    if not links:
        Notify(settings.PLEDGE_HOOK).alert(Notify.warn(f"No links crawled from {start} to {end} \nChange the cause or the range"))
        return
    
    
    for link in links:
        try:
            with transaction.atomic():
                PledgeIndexedUrl.objects.create(url=link)
        # check for duplicate entry error
        except IntegrityError:
            Notify(settings.PLEDGE_HOOK).alert(Notify.warn(f"Duplicate entry error skipping: {link}"))
            continue        
        
        except Exception as e:
            Notify(settings.PLEDGE_HOOK).alert(Notify.error(f"Error saving {link}: {str(e)}"))
            continue
    return


@shared_task(name="crawl_pledge")
def crawl_pledge():
    logger = logging.getLogger(__name__)
    cursor = CrawlCursor.objects.get_or_create(app="pledge", max_cursor=3000)[0]
    if  cursor.current_cursor >= cursor.max_cursor:
        cursor.current_cursor = cursor.max_cursor
        cursor.save()
        Notify(settings.PLEDGE_HOOK).alert(Notify.success("Url Crawling complete"))
        logger.info("SUCCESS: Crawling complete")
        return
    start = cursor.current_cursor + 1
    end = cursor.current_cursor + cursor.increment
    end = min(end, cursor.max_cursor)
    do_url_indexing.delay(start, end)
    cursor.current_cursor = end
    cursor.save()
    logger.info(f"SUCCESS: Crawled from {start} to {end}")
    # Notify(settings.PLEDGE_HOOK).alert(Notify.success(f"Crawled from {start} to {end}"))
    return
    
    
@shared_task(name="scraper_pledge")
def scrape_pledge_data(url, id):
    HOOK = settings.PLEDGE_HOOK
    logger = logging.getLogger(__name__)
    try:
        spider = PledgeScraper(url)
        data = spider.scrape()
        if data.get("image", None) is None:
            raise Exception("No image found")
        NGO.objects.filter(id=id).update(resolved=True, locked=True, image=data["image"])
        logger.info(f"SUCCESS: Scraped {url}")
    # skip in place of duplicate entry error
    except IntegrityError:
        Notify(HOOK).alert(Notify.warn(f"Duplicate entry error skipping: {url}"))
        
    except Exception as e:
        logger.error(f"ERROR: {url} - {str(e)}")
        Notify(HOOK).alert(Notify.error(f"{url} \n{str(e)}"))
    return 


@shared_task(name="start_scraping")
def scrape_orchestration():
    first_ten = PledgeIndexedUrl.objects.filter(is_scraped=False, 
                                                locked=False,
                                                trial__lte=6
                                                )[:50]
    if not first_ten:
        Notify(settings.PLEDGE_HOOK).alert(Notify.info("No more urls to scrape"))
        return
    for url in first_ten:
        scrape_url = url.url
        url.locked = True
        url.save()
        scrape_pledge_data.delay(url=scrape_url)
    return

@shared_task(name="start_scraping_2")
def scrape_orchestration_2():
    to_scrape = NGO.objects.filter(resolved=False, locked=False)[:10]
    if not to_scrape:
        Notify(settings.PLEDGE_HOOK).alert(Notify.info("No more urls to scrape"))
        return
    for ngo in to_scrape:
        url = reverse_list(ngo.urls_scraped)[0]
        ngo.locked = True
        ngo.save()
        scrape_pledge_data.delay(url=url, id=ngo.id)
    return

@shared_task(name="report_pledge")
def report_pledge():
    total = PledgeIndexedUrl.objects.count()
    scraped = PledgeIndexedUrl.objects.filter(is_scraped=True).count()
    failing = PledgeIndexedUrl.objects.filter(is_scraped=False, locked=False, trial__gt=4).count()
    Notify(settings.PLEDGE_HOOK).alert(Notify.info(f"Total URL Indexed: {total} \nScraped: {scraped} \nFailing: {failing}"))
    return
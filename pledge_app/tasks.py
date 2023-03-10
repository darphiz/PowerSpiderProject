import logging
from contextlib import suppress
from celery import shared_task
from ngo_scraper.notification import Notify
from .services import PledgeListCrawler, PledgeScraper
from .models import PledgeIndexedUrl, CrawlCursor, NGO
from django.db import transaction
from django.utils.timezone import now
from django.conf import settings
from django.db.utils import IntegrityError


@shared_task(name="do_url_indexing")
def do_url_indexing(start, end):
    try:
        spider = PledgeListCrawler(start=start, end=end, cause="animals")
        links = spider.crawl_all()
    except Exception as e:
        Notify(settings.PLEDGE_HOOK).alert(Notify.error(f"Error crawling from {start} to {end}: {str(e)}"))
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
    Notify(settings.PLEDGE_HOOK).alert(Notify.success(f"Crawled from {start} to {end}"))
    return
    
    
@shared_task(name="scraper_pledge")
def scrape_pledge_data(url):
    HOOK = settings.PLEDGE_HOOK
    logger = logging.getLogger(__name__)
    try:
        spider = PledgeScraper(url)
        data = spider.scrape()
        with transaction.atomic():
            NGO.objects.update_or_create(**data)
            PledgeIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        logger.info(f"SUCCESS: Scraped {url}")
    # skip in place of duplicate entry error
    except IntegrityError:
        Notify(HOOK).alert(Notify.warn(f"Duplicate entry error skipping: {url}"))
        PledgeIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        
    
    except Exception as e:
        with suppress(Exception):
            update_url = PledgeIndexedUrl.objects.get(url=url)
            update_url.trial += 1
            update_url.is_scraped = False
            update_url.locked = False
            update_url.save()
        logger.error(f"ERROR: {url} - {str(e)}")
        Notify(HOOK).alert(Notify.error(f"{url} \n{str(e)}"))
    return 


@shared_task(name="start_scraping")
def scrape_orchestration():
    first_ten = PledgeIndexedUrl.objects.filter(is_scraped=False, 
                                                locked=False,
                                                trial__lte=4
                                                )[:10]
    if not first_ten:
        Notify(settings.PLEDGE_HOOK).alert(Notify.info("No more urls to scrape"))
        return
    for url in first_ten:
        scrape_url = url.url
        url.locked = True
        url.save()
        scrape_pledge_data.delay(url=scrape_url)
    return


@shared_task(name="report_pledge")
def report_pledge():
    total = PledgeIndexedUrl.objects.count()
    scraped = PledgeIndexedUrl.objects.filter(is_scraped=True).count()
    failing = PledgeIndexedUrl.objects.filter(is_scraped=False, locked=False, trial__gt=4).count()
    Notify(settings.PLEDGE_HOOK).alert(Notify.info(f"Total URL Indexed: {total} \nScraped: {scraped} \nFailing: {failing}"))
    return
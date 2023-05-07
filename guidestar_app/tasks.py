import re
import logging
from celery import shared_task
from guidestar_app.models import CrawlCursor, GuideStarIndexedUrl, NGO
from guidestar_app.services import GuideStarIndexer, GuideStarScraper
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from django.conf import settings

from ngo_scraper.notification import Notify


log = logging.getLogger(__name__)
HOOK = settings.GUIDESTAR_HOOK
notification = Notify(HOOK)


@shared_task(name="index_guidestar_url")
def index_guidestar_url():
    cursor = CrawlCursor.objects.get_or_create(app="guidestar", max_cursor=20000)[0]
    if  cursor.current_cursor >= cursor.max_cursor:
        cursor.current_cursor = cursor.max_cursor
        cursor.save()
        log.info("SUCCESS: Crawling complete")
        return
    start = cursor.current_cursor
    end = cursor.current_cursor + cursor.increment
    end = min(end, cursor.max_cursor)
    spider = GuideStarIndexer(start, end)
    links = spider.crawl()
    for link in links:
        try:
            with transaction.atomic():
                GuideStarIndexedUrl.objects.create(url=link)
        except Exception as e:
            log.error(f"Error saving {link}: {str(e)}")
            notification.alert(
                Notify.error(
                    f"Error saving {link}: \n{str(e)}"
                )
            )
            continue

    cursor.current_cursor = end
    cursor.save()
    log.info(f"SUCCESS: Crawled from {start} to {end}")
    return


@shared_task(name="scrape_guidestar_data")
def scrape_guidestar_data(url, init_data=None):
    try:
        spider = GuideStarScraper(url, initial_data=init_data)
        data = spider.scrape()
        if not data:
            log.error(f"ERROR: {url} - No data found")
            GuideStarIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
            return
        NGO.objects.create(**data)
        GuideStarIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        log.info(f"SUCCESS: Scraped {url}")
    except IntegrityError as e:
        log.error(f"ERROR: {url} - {str(e)}")
        GuideStarIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        return
    
    except Exception as e:
        try:
            indexed_url = GuideStarIndexedUrl.objects.get(url=url)
            indexed_url.is_scraped = False
            indexed_url.locked = False
            indexed_url.trial = indexed_url.trial + 1
            indexed_url.save()
        except GuideStarIndexedUrl.DoesNotExist:
            pass
        except Exception as e:
            log.error(f"ERROR: {url} - {str(e)}")
            notification.alert(
                Notify.error(
                    f"ERROR: {url}: \n{str(e)}"
                )
            )
        log.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
                Notify.error(
                    f"ERROR: {url}: \n{str(e)}"
                )
            )
    return

@shared_task(name="re_scrape_guidestar_data")
def re_scrape_guidestar_data(url, d_ein):
    try:
        spider = GuideStarScraper()
        data = spider.scrape_image_only(url)
        if not data:
            log.error(f"ERROR: {url} - No data found")
            return
        try:
            ein = data["govt_reg_number"]
            ng = NGO.objects.get(govt_reg_number=ein)
            ng.image = data["image"]
            ng.resolved = True
            ng.save()
        except NGO.DoesNotExist:
            pass
        
        except Exception as e:
            NGO.objects.filter(govt_reg_number=d_ein).update(resolved=False, locked=False)
            log.error(f"ERROR: {url} - {str(e)}")
            notification.alert(
                Notify.error(
                    f"ERROR: {url}: \n{str(e)}"
                )
            )
        log.info(f"SUCCESS: Scraped {url}")
    except Exception as e:
        NGO.objects.filter(govt_reg_number=d_ein).update(resolved=False, locked=False)
        log.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
                Notify.error(
                    f"ERROR: {url}: \n{str(e)}"
                )
            )
    return


@shared_task(name="start_scraping_guidestar")
def guide_star_orchestration():
    first_ten = GuideStarIndexedUrl.objects.filter(is_scraped=False, 
                                                   locked=False,
                                                   trial__lt=6
                                                   )[:25]
    for url in first_ten:
        scrape_url = url.url
        url.locked = True
        url.save()
        data = {
            "organization_name": url.organization_name,
            "govt_reg_number": url.govt_reg_number,
            "state": url.state
        }
        scrape_guidestar_data.delay(url=scrape_url, init_data=data)
    return

def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)

@shared_task(name="start_scraping_guidestar_v2")
def start_scraping_guidestar_v2():
    chunk = NGO.objects.filter(image__isnull=False, resolved=False, locked=False)[:25]
    for ngo in chunk:
        scrape_url = reverse_list(ngo.urls_scraped)[0]
        ngo.locked = True
        ngo.save()
        ein = ngo.govt_reg_number
        re_scrape_guidestar_data.delay(url=scrape_url, d_ein=ein)
    return
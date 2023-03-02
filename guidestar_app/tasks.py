from celery import shared_task
from guidestar_app.models import CrawlCursor, GuideStarIndexedUrl, NGO
from guidestar_app.services import GuideStarIndexer, GuideStarScraper
from django.db import transaction
from ngo_scraper.loggers import guide_star_log
from django.utils.timezone import now



@shared_task(name="index_guidestar_url")
def index_guidestar_url():
    log = guide_star_log()
    cursor = CrawlCursor.objects.get_or_create(app="guidestar", max_cursor=20)[0]
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
            continue

    cursor.current_cursor = end
    cursor.save()
    log.info(f"SUCCESS: Crawled from {start} to {end}")
    return


@shared_task(name="scrape_guidestar_data")
def scrape_guidestar_data(url):
    log = guide_star_log()
    try:
        spider = GuideStarScraper(url)
        data = spider.scrape()
        with transaction.atomic():
            NGO.objects.update_or_create(**data)
            GuideStarIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        log.info(f"SUCCESS: Scraped {url}")
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
        log.error(f"ERROR: {url} - {str(e)}")
    return



@shared_task(name="start_scraping_guidestar")
def guide_star_orchestration():
    first_ten = GuideStarIndexedUrl.objects.filter(is_scraped=False, 
                                                   locked=False,
                                                   trial__lt=4
                                                   )[:20]
    for url in first_ten:
        scrape_url = url.url
        url.locked = True
        url.save()
        scrape_guidestar_data.delay(url=scrape_url)
    return
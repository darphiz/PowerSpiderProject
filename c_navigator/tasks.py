import logging
from contextlib import suppress
from celery import shared_task
from django.db import transaction
from ngo_scraper.notification import Notify
from django.conf import settings
from c_navigator.services import CharityNavigatorScraper
from .models import CrawlCursor, NGO, FailedPages

logger = logging.getLogger(__name__)

MAX_PAGE = 2000
notification = Notify(settings.CHARITY_HOOK)

def track_failed_pages(page, error):
    with suppress(Exception):
        with transaction.atomic():
            FailedPages.objects.update_or_create(page=page, error=error, locked=False)


@shared_task(name="do_data_scraping")
def do_data_scraping(page, retry=False):
    try:
        spider = CharityNavigatorScraper(page)
        data = spider.crawl()
        if retry:
            with transaction.atomic():
                FailedPages.objects.filter(page=page).delete()
    except Exception as e:
        logger.error(f"ERROR: {page} - {str(e)}")
        notification.alert(
            Notify.error(
                f"Page - {page}  \nTraceback: \n{str(e)}"
            )
        )
        track_failed_pages(page, str(e))
        return

    try:
        with transaction.atomic():
            for d in data:
                NGO.objects.update_or_create(
                    organization_name=d["organization_name"],
                    defaults={**d}
                    )
    except Exception as e:
        logger.error(f"ERROR: {page} - {str(e)}")
        notification.alert(
            Notify.error(
                f"Page - {page}  \nTraceback: \n{str(e)}"
            )
        )
        track_failed_pages(page, str(e))
        return


@shared_task(name="crawl_charity_data")
def crawl_charity_data(page):
    try:
        do_data_scraping.delay(page)
        cursor = CrawlCursor.objects.get_or_create(app="charity", max_cursor=MAX_PAGE)[0]
        cursor.current_page = cursor.current_page + 1
        cursor.save()
    except Exception as e:
        logger.error(f"ERROR: {page} - {str(e)}")
        notification.alert(
            Notify.error(
                f"Page - {page}  \nTraceback: \n{str(e)}"
            )
        )
        track_failed_pages(page, str(e))
        return
        
        
@shared_task(name="start_scraping_charity")
def charity_orchestrator():
    cursor = CrawlCursor.objects.get_or_create(app="charity", max_cursor=MAX_PAGE)[0]
    if  cursor.current_page >= cursor.max_cursor:
        cursor.current_page = cursor.max_cursor
        cursor.save()
        notification.alert(
            Notify.info(
                "No more data to crawl"
            )
        )    
        return
    crawl_charity_data.delay(cursor.current_page)
    # notification.alert(
    #     Notify.info(
    #         f"Started crawling page {cursor.current_page} of {cursor.max_cursor}"
    #     )
    # )
    return
    
    
@shared_task(name="charity_retry_failed_pages")
def charity_retry_failed_pages():
    if one_failed_page := FailedPages.objects.filter(
        trial__lt=4, locked=False
    ).first():
        one_failed_page.locked = True
        one_failed_page.trial = one_failed_page.trial + 1
        one_failed_page.save()
        notification.alert(
            Notify.info(
                f"Retrying page {one_failed_page.page} of {one_failed_page.trial} times"
            )
        )
        do_data_scraping.delay(one_failed_page.page, retry=True)
        return
    return

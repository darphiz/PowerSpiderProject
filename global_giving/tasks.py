import logging
from celery import shared_task
from .services import GlobalGivingScraper
from .models import GlobalGivingNGO, GlobalGivingIndexedUrl
from django.db import transaction, IntegrityError
from django.conf import settings
from ngo_scraper.notification import Notify
from django.db.models import F


logger = logging.getLogger(__name__)
GG_HOOK = settings.GLOBALGIVING_HOOK
notification = Notify(GG_HOOK)

@shared_task(name="scrape_global_giving")
def scrape_global_giving(url):
    if not url:
        logger.error("ERROR: No URL provided")
        return
    
    try:
        bot = GlobalGivingScraper(url)
        data = bot.crawl() 
        with transaction.atomic():
            GlobalGivingNGO.objects.create(**data)
            GlobalGivingIndexedUrl.objects.filter(url=url).update(is_scraped=True)
            logger.info(f"SUCCESS: Scraped {url}")
            
    except IntegrityError as e:
        # skip if already exists
        GlobalGivingIndexedUrl.objects.filter(url=url).update(is_scraped=True)
        logger.info(f"Skipping: Scraped {url}")

            
    except Exception as e:
        GlobalGivingIndexedUrl.objects.filter(url=url).update(
                is_scraped=False,
                locked=False,
                trial= F("trial") + 1
                )
        logger.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
            Notify.error(
                f"ERROR: {url} \n{str(e)}"
            )
        )
        
    return



@shared_task(name="start_scraping_gg")
def task_orchestrator():
    try:
        first_ten = GlobalGivingIndexedUrl.objects.filter(
                is_scraped=False, 
                locked=False,
                trial__lte=5
                )[:10]
        for url in first_ten:
            scrape_url = url.url
            url.locked = True
            url.trial += 1
            url.save()
            scrape_global_giving.delay(url=scrape_url)
        logger.info(f"Started scraping {len(first_ten)} urls")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        notification.alert(
            Notify.error(
                f"ERROR: {url} \n{str(e)}"
            )
        )
    return
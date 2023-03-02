from celery import shared_task
from .services import GlobalGivingScraper
from .models import GlobalGivingNGO, GlobalGivingIndexedUrl
from django.db import transaction
from ngo_scraper.loggers import gg_log


@shared_task(name="scrape_global_giving")
def scrape_global_giving(url):
    logger = gg_log()
    if not url:
        logger.error("ERROR: No URL provided")
        return
    
    try:
        bot = GlobalGivingScraper(url)
        data = bot.crawl() 
        with transaction.atomic():
            GlobalGivingNGO.objects.update_or_create(**data)
            GlobalGivingIndexedUrl.objects.filter(url=url).update(is_scraped=True)
            logger.info(f"SUCCESS: Scraped {url}")
    except Exception as e:
        GlobalGivingIndexedUrl.objects.filter(url=url).update(is_scraped=False)
        logger.error(f"ERROR: {url} - {str(e)}")
        
    return



@shared_task(name="start_scraping_gg")
def task_orchestrator():
    logger = gg_log()
    try:
        first_ten = GlobalGivingIndexedUrl.objects.filter(is_scraped=False, locked=False)[:10]
        for url in first_ten:
            scrape_url = url.url
            url.locked = True
            url.save()
            scrape_global_giving.delay(url=scrape_url)
        logger.info(f"Started scraping {len(first_ten)} urls")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
    return
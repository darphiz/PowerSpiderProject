import logging
from celery import shared_task
from fcra_app.models import FCR_Cursor, FCR_NGO
from fcra_app.services import FCRA_Scraper
from django.db import transaction
from django.conf import settings
from ngo_scraper.notification import Notify

HOOK = settings.FRCA_HOOK
logger = logging.getLogger(__name__)
    

@shared_task(name="fcr_scrapper")
def scrape_data(uid, state_name, state_id, state_year):
    notification = Notify(HOOK)
    scraper = FCRA_Scraper(
            state_name = state_name, 
            state_id = state_id, 
            state_year=state_year
        )
    if all_data := scraper.crawl():
        try:
            with transaction.atomic():
                for d_point in all_data:
                    FCR_NGO.objects.update_or_create(**d_point)        
            FCR_Cursor.objects.filter(id=uid).update(is_scraped=True)
            logger.info(f"SUCCESS: Scraped {state_name} -{state_year}")
        except Exception as e:
            FCR_Cursor.objects.filter(id=uid).update(is_scraped=False)
            logger.error(f"ERROR: {state_name} -{state_year} - {str(e)}")
            notification.alert(
                Notify.error(f"{state_name} -{state_year} - {str(e)}")
            )
    else:
        FCR_Cursor.objects.filter(id=uid).update(is_scraped=True)
        logger.warning(f"INFO: Scraped {state_name} -{state_year} with no data")
        notification.alert(
            Notify.info(f"Scraped {state_name} -{state_year} with no data")
        )
    return

@shared_task(name="start_scraping_fcr")
def fcr_task_orchestrator():
    try:
        first_ten = FCR_Cursor.objects.filter(is_scraped=False, locked=False)[:10]
        for data_point in first_ten:
            data_point.locked = True
            data_point.save()
            state_name = data_point.state
            state_id = data_point.state_id
            state_year = data_point.year
            uid = data_point.id
            scrape_data.delay(uid, state_name, state_id, state_year)
        logger.info(f"Started scraping {len(first_ten)} urls")
    except Exception as e:
        logger.error(f"ERROR: {str(e)}")
        Notify(HOOK).alert(Notify.error(str(e)))
    return

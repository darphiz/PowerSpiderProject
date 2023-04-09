import logging
from celery import shared_task
from global_giving_india.services import GG_India_Scraper
from django.db import IntegrityError
from .models import GuideStarIndiaIndexedUrl, NGO
from django.utils.timezone import now
from ngo_scraper.notification import Notify
from django.conf import settings

logger = logging.getLogger(__name__)
HOOK = settings.GGI_HOOK

@shared_task(name="scrape_ggi_data")
def scrape_ggi_data(url):
    
    try:
        notification = Notify(HOOK)
        spider = GG_India_Scraper(url)
        data = spider.scrape()
        # with transaction.atomic():
        NGO.objects.create(**data)
        GuideStarIndiaIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        logger.info(f"SUCCESS: Scraped {url}")
    # except duplicate key error
    except IntegrityError as e:
        logger.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
            Notify.error(f"{url} \nSKIPPED: Duplicate key error")
        )
        GuideStarIndiaIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
    except Exception as e:
        try:
            indexed_url = GuideStarIndiaIndexedUrl.objects.get(url=url)
            indexed_url.is_scraped = False
            indexed_url.locked = False
            indexed_url.trial = indexed_url.trial + 1
            indexed_url.save()
        except GuideStarIndiaIndexedUrl.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"ERROR: {url} - {str(e)}")
            notification.alert(
                Notify.error(f"{url} \n{str(e)}")
            )
            
            
        logger.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
            Notify.error(f"{url} \n{str(e)}")
        )
    return


@shared_task(name="start_scraping_ggi")
def ggi_orchestration():
    notification = Notify(HOOK)
    first_ten = GuideStarIndiaIndexedUrl.objects.filter(is_scraped=False, 
                                                   locked=False,
                                                   trial__lt=5
                                                   )[:10]
    
    if first_ten.count() == 0:
        notification.alert(
            Notify.info("No more urls to scrape")
        )
        return
    
    for url in first_ten:
        scrape_url = url.url
        url.locked = True
        url.save()
        scrape_ggi_data.delay(url=scrape_url)
    return
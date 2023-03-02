from celery import shared_task
from irs_app.models import IRSIndexedUrl, NGO, XMLUrlIndexer
from irs_app.services import IrsScraper, IrsUrlIndexer
from django.db import transaction
from irs_app.xml_services import XMLUrlSpider, XMLScraper
from ngo_scraper.loggers import guide_star_log
from django.utils.timezone import now


@shared_task(name="index_irs_url")
def irs_url_indexer():
    spider = IrsUrlIndexer()
    spider.crawl()
    return

@shared_task(name="scrape_irs_data")
def scrape_irs(url):
    log = guide_star_log()
    try:
        scraper = IrsScraper(url)
        data = scraper.scrape()
        with transaction.atomic():
            NGO.objects.create(**data)
            IRSIndexedUrl.objects.filter(url=url).update(is_scraped=True, scraped_on=now())
        log.info(f"SUCCESS: Scraped {url}")
    except Exception as e:   
        try:
            indexed_url = IRSIndexedUrl.objects.get(url=url)
            indexed_url.is_scraped = False
            indexed_url.locked = False
            indexed_url.trial = indexed_url.trial + 1
            indexed_url.save()
        except IRSIndexedUrl.DoesNotExist:
            pass
        except Exception as e:
            log.error(f"ERROR: {url} - {str(e)}")
        log.error(f"ERROR: {url} - {str(e)}")
    return
    
@shared_task(name="start_scraping_irs")
def task_orchestrator():
    first_30 = IRSIndexedUrl.objects.filter(
                    is_scraped = False, 
                    locked=False,
                    trial__lt=4
                    )[:20]
    for url in first_30:
        scrape_url = url.url
        url.locked = True
        url.save()
        scrape_irs.delay(scrape_url)
   
   
   
 
 
#################################################################        
        
        
"""
IRS XML
"""

@shared_task(name="index_irs_xml_url")
def xml_downloader():
    if one_url := XMLUrlIndexer.objects.filter(
        is_downloaded=False,
        is_scraped=False, 
        locked=False, 
        trial__lt=4
    ).first():
        one_url.locked = True
        one_url.save()
        XMLUrlSpider.download_xml_file(one_url.url)
    return

@shared_task(name="start_scraping_irs_xml")
def xml_task_orchestrator():
    if one_url := XMLUrlIndexer.objects.filter(
        is_downloaded=True,
        is_scraped=False,
        locked=False, 
        trial__lt=4
    ).first():
        one_url.locked = True
        one_url.save()
        scrape_irs_xml.delay(one_url.url)
    return




@shared_task(name="scrape_irs_xml_data")
def scrape_irs_xml(url):
    log = guide_star_log()
    try:
        scraper = XMLScraper(url)
        scraper.scrape()
        with transaction.atomic():
            XMLUrlIndexer.objects.filter(url=url).update(is_scraped=True, is_downloaded=True, scraped_on=now())
        log.info(f"SUCCESS: Scraped {url}")
    except Exception as e:   
        try:
            indexed_url = XMLUrlIndexer.objects.get(url=url)
            indexed_url.is_scraped = False
            indexed_url.is_downloaded = False
            indexed_url.locked = False
            indexed_url.trial = indexed_url.trial + 1
            indexed_url.save()
        except XMLUrlIndexer.DoesNotExist:
            pass
        except Exception as e:
            log.error(f"ERROR: {url} - {str(e)}")
        log.error(f"ERROR: {url} - {str(e)}")
    return
    
    
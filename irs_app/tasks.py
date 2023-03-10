import re
import logging
from celery import shared_task
from irs_app.models import IRSIndexedUrl, NGO, XMLUrlIndexer
from irs_app.services import IrsScraper, IrsUrlIndexer
from django.db import transaction
from irs_app.xml_services import XMLUrlSpider, XMLScraper
from django.utils.timezone import now
from django.conf import settings
from ngo_scraper.notification import Notify

IRS_HOOK = settings.IRS_HOOK
log = logging.getLogger(__name__) 
notification = Notify(IRS_HOOK)


def format_list(lists):
    try:
        if not lists:
            return None
        if not isinstance(lists, list):
            lists = [lists]
        _set = {"\"" + x + "\"" for x in lists}
        _set = str(_set).replace("'", "")
        return _set
    except Exception:
        return None
    
def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)
        

        
@shared_task(name="index_irs_url")
def irs_url_indexer():
    spider = IrsUrlIndexer()
    spider.crawl()
    return

@shared_task(name="scrape_irs_data")
def scrape_irs(url):
    try:
        scraper = IrsScraper(url)
        data = scraper.scrape()
        with transaction.atomic():
            if not data["organization_name"]:
                return
            ngo_data, created = NGO.objects.update_or_create(
                organization_name=data["organization_name"],
                defaults={**data}
            )  
            
            if not created:
                last_url = reverse_list(ngo_data.domain)
                new_url = ["data-download-epostcard.zip", ]
                unique_urls = list(set(last_url + new_url))
                new_domain_string = format_list(unique_urls)
                ngo_data.domain = new_domain_string
                
                ## urls scraped
                
                last_url_scraped = reverse_list(ngo_data.urls_scraped)
                new_url_scraped = ["data-download-epostcard.txt", ]
                unique_urls_scraped = list(set(last_url_scraped + new_url_scraped))
                new_url_scraped_string = format_list(unique_urls_scraped)
                ngo_data.urls_scraped = new_url_scraped_string
                # save
                ngo_data.save()  
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
            notification.alert(
                Notify.error(
                    f"ERROR: {url} \n{str(e)}"
                )
            )
        log.error(f"ERROR: {url} - {str(e)}")
        notification.alert(
                Notify.error(
                    f"ERROR: {url} \n{str(e)}"
                )
            )
    return
    
@shared_task(name="start_scraping_irs")
def task_orchestrator():
    first_20 = IRSIndexedUrl.objects.filter(
                    is_scraped = False, 
                    locked=False,
                    trial__lt=6
                    )[:20]
    for url in first_20:
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
    
    
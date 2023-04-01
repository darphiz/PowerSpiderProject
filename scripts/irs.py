from contextlib import suppress
import os
from irs_app.xml_services import XMLScraper, XMLUrlSpider
from irs_app.models import XMLUrlIndexer, NGO, IRSIndexedUrl 
from django.core.paginator import Paginator
from ngo_scraper.notification import Notify
from django.conf import settings
from irs_app.services import IrsUrlIndexer 

IRS_HOOK = settings.IRS_HOOK


def un_scrape():
    all_urls = XMLUrlIndexer.objects.all()
    all_urls.update(is_scraped=False, scraped_on=None, locked=False, is_downloaded=False)
    print("All URLs have been reset")
    return


def re_index_irs():
    all_urls = IRSIndexedUrl.objects.filter(
        is_scraped=False, locked=True
    )
    all_urls.update(is_scraped=False, scraped_on=None, locked=False)
    print("All URLs have been reset")
    
    


def scrape(ngo):
    if not ngo.is_downloaded:
        print(f"Downloading {ngo.url} ...")
        XMLUrlSpider.download_xml_file(ngo.url)
    print(f"Scraping {ngo.url} ...")
    XMLScraper(ngo.url).scrape()
    ngo.is_scraped = True
    ngo.save()
    print(f"Scraping {ngo.url} completed")

def delete_file_from_folder(file_name):
    with suppress(Exception):
        folder = 'irs_app/irs_xml/'
        file_path = os.path.join(folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_name}")


def start_scraping_xml(page, page_size=3):
    notification = Notify(IRS_HOOK)
    try:
        all_urls = XMLUrlIndexer.objects.all().order_by('id')
        paginated = Paginator(all_urls, page_size)
        page_obj = paginated.page(page)
        for ngo in page_obj.object_list:
            notification.alert(
                Notify.info(
                    f"Pick up scraping {ngo.url}"
                )
            )
            if not ngo.is_scraped:
                scrape(ngo)
            notification.alert(
                Notify.info(
                    f"Scraping {ngo.url} completed",
                )
            )
        notification.alert(
                Notify.info(
                    f"Scraping completed for page {page}",
                ))
    except Exception as e:
        print(e)
        notification.alert(
                Notify.info(
                    f"Scraping failed for page {page} \n {str(e)}",
                ))
    return



def scrape_zip_file():
    notification = Notify(IRS_HOOK)
    scraper = IrsUrlIndexer()
    scraper.crawl()
    notification.alert(
        Notify.info("Scraping completed for zip files")
    )
    return



def scrape_page(page, page_size=3):
    all_urls = XMLUrlIndexer.objects.all().order_by('id')
    all_urls = []
    for ngo in all_urls:
        if not ngo.is_downloaded:
            print(f"Downloading {ngo.url} ...")
            XMLUrlSpider.download_xml_file(ngo.url) 
        # print(f"Downloading {ngo.url} ...")
        # print(f"Scraping {ngo.url} ...")
        total = XMLScraper(ngo.url).scrape()
        ngo.is_downloaded = True
        ngo.save()
    return

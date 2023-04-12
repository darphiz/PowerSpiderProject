from random import randint
from time import sleep
from contextlib import suppress
from c_navigator.services import CharityNavigatorScraper
from ngo_scraper.notification import Notify
from django.conf import settings
from c_navigator.models import LastPage, NGO
from scripts.charity_builders import beacon_only_builder, cause_only_builder, ratings_only_builder, state_only_builder
from scripts.c_data import states, beacons

CHARITY_HOOK = settings.CHARITY_HOOK


notification = Notify(CHARITY_HOOK)
result_size = 15

def q_builder(cause:str, state:str, result_size:int = result_size, page:int = 1):
    return {
        'query': f'''
            query PublicSearchFaceted {{
                publicSearchFaceted(
                    causes: ["{cause}"], 
                    states: ["{state}"]
                    result_size: {result_size},
                    from: {(page * result_size) - result_size}
                ) {{
                    result_count
                    results {{
                        ein
                        name
                        mission
                        organization_url
                        charity_navigator_url
                        cause
                        street
                        street2
                        city
                        state
                        zip
                        country
                    }}
                }}
            }}
        '''
    }






def save_data(all_data: list):
    if not all_data:
        return
    with suppress(Exception):
        print(f"Saving {len(all_data)} records")
        bulk_data = [NGO(**data) for data in all_data]
        NGO.objects.bulk_create(bulk_data, ignore_conflicts=True)
    return


def single_scrape_data(builder, payload):        
    for cause in payload:
        max_query = builder(cause)
        spider = CharityNavigatorScraper()
        max_result = spider.get_max_result(max_query) or 1000
        page_range = int(max_result // result_size)
        pages = page_range if page_range <= 1000 else 800
        start_page = 1
        for page in range(start_page, pages + 1):
            sleep_time = randint(1, 4)
            try:
                print(f"Scraping page {page} of {pages} for {cause}")
                query = builder(cause, page=page)
                data = spider.crawl(query)
                save_data(data)    
                print(f"Sleeping for {sleep_time} seconds")
            except Exception as e:
                print(f"Error: {str(e)}")
                notification.alert(
                    Notify.error(
                        f"Page - {page}  \nTraceback: \n{str(e)}"
                    )
                )
                print(f"Sleeping for {sleep_time} seconds")
            sleep(sleep_time)
       
             
    notification.alert(
        Notify.info(
            f"Finished scraping all data"
        )
    )
    return


def scrape_cause_only():
    with open('scripts/charity_causes.txt', 'r') as f:
        payload = f.read().splitlines()

    builder = cause_only_builder
    single_scrape_data(builder, payload)
    
def scrape_state_only():
    payload = states 
    builder = state_only_builder
    single_scrape_data(builder, payload)

def scrape_beacon_only():
    payload = beacons
    builder = beacon_only_builder
    single_scrape_data(builder, payload)
    
def scrape_ratings_only():
    payload = [
        "1","2","3", "4"
    ]
    builder = ratings_only_builder
    single_scrape_data(builder, payload)
    
    
    

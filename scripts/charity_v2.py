from random import randint
from time import sleep
from contextlib import suppress
from c_navigator.services import CharityNavigatorScraper
from ngo_scraper.notification import Notify
from django.conf import settings
from c_navigator.models import  NGO
from scripts.charity_builders import beacon_only_builder, beacon_ratings_builder, cause_beacon_builder, cause_beacon_ratings_builder, cause_only_builder, cause_ratings_builder, ratings_only_builder, state_beacon_builder, state_beacon_ratings_builder, state_cause_beacon_builder, state_cause_beacon_ratings_builder, state_cause_ratings_builder, state_only_builder, state_ratings_builder
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



def log(file_name, data):
    with open(file_name, 'w') as f:
        f.write(data)
        
    


def save_data(all_data: list):
    if not all_data:
        print("No data to save")
        return 0 
    with suppress(Exception):
        total_unique_data = len(all_data) 
        print(f"Saving {total_unique_data} records")
        bulk_data = [NGO(**data) for data in all_data]
        NGO.objects.bulk_create(bulk_data, ignore_conflicts=True)
    return total_unique_data


def single_scrape_data(builder, payload,file_name: str = 'scripts/last_page_.txt'):        
    total_unique_data = 0
    for cause in payload:
        max_query = builder(cause)
        spider = CharityNavigatorScraper()
        max_result = spider.get_max_result(max_query) or 1000
        page_range = int(max_result // result_size)
        pages = page_range if page_range <= 1000 else 800
        start_page = 1
        for page in range(start_page, pages + 1):
            scrape_spider = CharityNavigatorScraper()
            # sleep_time = randint(1, 4)
            try:
                print(f"Scraping page {page} of {pages} for {cause}")
                log(file_name, f"{cause} - {page}")
                
                query = builder(cause, page=page)
                res_data = scrape_spider.crawl(query)
                total_saved = save_data(res_data)    
                    
                # print(f"Sleeping for {sleep_time} seconds")
            except Exception as e:
                print(f"Error: {str(e)}")
                notification.alert(
                    Notify.error(
                        f"Page - {page}  \nTraceback: \n{str(e)}"
                    )
                )
                total_saved = 0
            total_unique_data = total_unique_data + total_saved
            print(f"Total unique data: {total_unique_data}")
                
                # print(f"Sleeping for {sleep_time} seconds")
            # sleep(sleep_time)
       
             
    notification.alert(
        Notify.info(
            f"Finished scraping all data"
        )
    )
    return


def double_scrape_data(builder, payload_1, payload_2, file_name: str = 'scripts/last_double_page.txt'):
    total_unique_data = 0
    for p_1 in payload_1:
        for p_2 in payload_2:
            max_query = builder(p_1, p_2)
            spider = CharityNavigatorScraper()
            max_result = spider.get_max_result(max_query) or 1000
            page_range = int(max_result // result_size)
            pages = page_range if page_range <= 1000 else 800
            start_page = 1
            for page in range(start_page, pages + 1):
                scrape_spider = CharityNavigatorScraper()
                # sleep_time = randint(1, 4)
                try:
                    print(f"Scraping page {page} of {pages} for {p_1} - {p_2}")
                    log(file_name, f"{p_1} - {p_2} - {page}")
                    query = builder(p_1, p_2, page=page)
                    res_data = scrape_spider.crawl(query)
                    total_saved = save_data(res_data)    
                    # print(f"Sleeping for {sleep_time} seconds")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    notification.alert(
                        Notify.error(
                            f"Page - {page}  \nTraceback: \n{str(e)}"
                        )
                    )
                total_unique_data = total_unique_data + total_saved
                print(f"Total unique data: {total_unique_data}")
                
                    # print(f"Sleeping for {sleep_time} seconds")
                # sleep(sleep_time)
       
             
    notification.alert(
        Notify.info(
            f"Finished scraping all data"
        )
    )
    return

def triple_scrape_data(builder, payload_1, payload_2, payload_3, file_name:str='scripts/last_double_page.txt'):
    total_unique_data = 0
    for p_1 in payload_1:
        for p_2 in payload_2:
            for p_3 in payload_3:
                max_query = builder(p_1, p_2, p_3)
                spider = CharityNavigatorScraper()
                max_result =  spider.get_max_result(max_query)
                page_range = int(max_result // result_size)
                if page_range is None:
                    page_range = 0
                pages = page_range if page_range <= 1000 else 800
                start_page = 1
                the_pages = pages + 2 if max_result > 0 else 1
                print(max_result)
                for page in range(start_page, the_pages):
                    scrape_spider = CharityNavigatorScraper()
                    # sleep_time = randint(1, 4)
                    try:
                        print(f"Scraping page {page} of {pages} for {p_1} - {p_2} - {p_3}")
                        log(file_name, f"{p_1} - {p_2} - {p_3} - {page}")
                        query = builder(p_1, p_2, p_3, page=page)
                        res_data = scrape_spider.crawl(query)
                        total_saved = save_data(res_data)    
                        # print(f"Sleeping for {sleep_time} seconds")
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        notification.alert(
                            Notify.error(
                                f"Page - {page}  \nTraceback: \n{str(e)}"
                            )
                        )
                    total_unique_data = total_unique_data + total_saved
                    print(f"Total unique data: {total_unique_data}")
                    
                        # print(f"Sleeping for {sleep_time} seconds")
                    # sleep(sleep_time)
           
                 
    notification.alert(
        Notify.info(
            f"Finished scraping all data"
        )
    )
    return

def quad_scrape_data(builder, payload_1, payload_2, payload_3, payload_4, file_name:str='scripts/last_double_page.txt'):
    total_unique_data = 0
    for p_1 in payload_1:
        for p_2 in payload_2:
            for p_3 in payload_3:
                for p_4 in payload_4:
                    max_query = builder(p_1, p_2, p_3, p_4)
                    spider = CharityNavigatorScraper()
                    max_result = spider.get_max_result(max_query)
                    page_range = int(max_result // result_size)
                    if page_range is None:
                        page_range = 0
                    pages = page_range if page_range <= 1000 else 800
                    start_page = 1
                    the_pages = pages + 2 if max_result > 0 else 1
                    print(max_result)
                    for page in range(start_page, the_pages):
                        scrape_spider = CharityNavigatorScraper()
                        # sleep_time = randint(1, 4)
                        try:
                            print(f"Scraping page {page} of {pages} for {p_1} - {p_2} - {p_3} - {p_4}")
                            log(file_name, f"{p_1} - {p_2} - {p_3} - {p_4} - {page}")
                            query = builder(p_1, p_2, p_3, p_4, page=page)
                            res_data = scrape_spider.crawl(query)
                            total_saved = save_data(res_data)    
                            # print(f"Sleeping for {sleep_time} seconds")
                        except Exception as e:
                            print(f"Error: {str(e)}")
                            notification.alert(
                                Notify.error(
                                    f"Page - {page}  \nTraceback: \n{str(e)}"
                                )
                            )
                        total_unique_data = total_unique_data + total_saved
                        print(f"Total unique data: {total_unique_data}")
                        
                            # print(f"Sleeping for {sleep_time} seconds")
                        # sleep(sleep_time)
               
                     
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
    single_scrape_data(builder, payload, file_name='scripts/cause_log.txt')
    
def scrape_state_only():
    payload = states 
    builder = state_only_builder
    single_scrape_data(builder, payload, file_name='scripts/state_log.txt')

def scrape_beacon_only():
    payload = beacons
    builder = beacon_only_builder
    single_scrape_data(builder, payload, file_name='scripts/beacon_log.txt')
    
def scrape_ratings_only():
    payload = [
        "1","2","3", "4"
    ]
    builder = ratings_only_builder
    single_scrape_data(builder, payload, file_name='scripts/ratings_log.txt')
    

def scrape_state_beacon():
    payload_1 = states 
    payload_2 = beacons
    builder = state_beacon_builder
    double_scrape_data(builder, payload_1, payload_2, file_name='scripts/state_beacon_log.txt')    
    
def scrape_state_ratings():
    payload_1 = states 
    payload_2 = ["1","2","3", "4"]
    builder = state_ratings_builder
    double_scrape_data(builder, payload_1, payload_2, file_name='scripts/state_ratings_log.txt')


def scrape_cause_beacon():
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_1 = f.read().splitlines()
    payload_2 = beacons
    builder = cause_beacon_builder
    double_scrape_data(builder, payload_1, payload_2, file_name='scripts/cause_beacon_log.txt')
    
def scrape_cause_ratings():
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_1 = f.read().splitlines()
    payload_2 = ["1","2","3", "4"]
    builder = cause_ratings_builder
    double_scrape_data(builder, payload_1, payload_2, file_name='scripts/cause_ratings_log.txt')
    
def scrape_beacon_ratings():
    payload_1 = beacons
    payload_2 = ["1","2","3", "4"]
    builder = beacon_ratings_builder
    double_scrape_data(builder, payload_1, payload_2, file_name='scripts/beacon_ratings_log.txt')
    
def scrape_state_cause_beacon():
    payload_1 = states 
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_2 = f.read().splitlines()
    payload_3 = beacons
    builder = state_cause_beacon_builder
    triple_scrape_data(builder, payload_1, payload_2, payload_3, file_name='scripts/state_cause_beacon_log.txt')
    
    
def scrape_state_cause_ratings():
    payload_1 = states 
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_2 = f.read().splitlines()
    payload_3 = ["1","2","3", "4"]
    builder = state_cause_ratings_builder
    triple_scrape_data(builder, payload_1, payload_2, payload_3, file_name='scripts/state_cause_ratings_log.txt')
    
def scrape_state_beacon_ratings():
    payload_1 = states 
    payload_2 = beacons
    payload_3 = ["1","2","3", "4"]
    builder = state_beacon_ratings_builder
    triple_scrape_data(builder, payload_1, payload_2, payload_3, file_name='scripts/state_beacon_ratings_log.txt')

def scrape_cause_beacon_ratings():
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_1 = f.read().splitlines()
    payload_2 = beacons
    payload_3 = ["1","2","3", "4"]
    builder = cause_beacon_ratings_builder
    triple_scrape_data(builder, payload_1, payload_2, payload_3, file_name='scripts/cause_beacon_ratings_log.txt')
    
def scrape_state_cause_beacon_ratings():
    payload_1 = states 
    with open('scripts/charity_causes.txt', 'r') as f:
        payload_2 = f.read().splitlines()
    payload_3 = beacons
    payload_4 = ["1","2","3", "4"]
    builder = state_cause_beacon_ratings_builder
    quad_scrape_data(builder, payload_1, payload_2, payload_3, payload_4, file_name='scripts/state_cause_beacon_ratings_log.txt')
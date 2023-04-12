from random import randint
from time import sleep
from contextlib import suppress
from c_navigator.services import CharityNavigatorScraper
from ngo_scraper.notification import Notify
from django.conf import settings
from c_navigator.models import LastPage, NGO

CHARITY_HOOK = settings.CHARITY_HOOK


notification = Notify(CHARITY_HOOK)
result_size = 20

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

def scrape_data(use_part_two: bool = False):
    states = [
        'AK',
        'AL',
        'AR',
        'AS',
        'AZ',
        'CA',
        'CO',
        'CT',
        'DC',
        'DE',
        'FL',
        'GA',
        'GU',
        'HI',
        'IA',
        'ID',
        'IL',
        'IN',
        'KS',
        'KY',
        'LA',
        'MA',
        'MD',
        'ME',
        'MI',
        'MN',
        'MO',
        'MP',
        'MS',
        'MT',
        'NA',
        'NC',
        'ND',
        'NE',
        'NH',
        'NJ',
        'NM',
        'NV',
        'NY',
        'OH',
        'OK'        
    ]
    part_two = [
        'OR',
        'PA',
        'PR',
        'RI',
        'SC',
        'SD',
        'TN',
        'TX',
        'UT',
        'VA',
        'VI',
        'VT',
        'WA',
        'WI',
        'WV',
        'WY',
    ]
    
    causes = ["Arts and culture", "Education", "Environment", "Health", "Technology", "Forensic science", "Public safety", "Public affairs", "Agriculture, fishing and forestry", "Religion", "Sports and recreation", "Human rights", "Human services", "International relations", "Unknown or not classified"]
    if not use_part_two:
        last_cursor = LastPage.objects.first()
        if not last_cursor:
            last_cursor = LastPage.objects.create(state=states[0], cause=causes[0], page=1)
    
        last_state = last_cursor.state
        last_causes = last_cursor.cause
        last_page = last_cursor.page
            
        states = states[states.index(last_state):]
        causes = causes[causes.index(last_causes):]
        print(f"Starting from {last_state} page {last_page} on {last_causes}")
    else:
        states = part_two
        
    for state in states:
        for cause in causes:
            max_query = q_builder(cause, state)
            spider = CharityNavigatorScraper()
            max_result = spider.get_max_result(max_query) or 1000
            page_range = int(max_result // result_size)
            pages = page_range if page_range <= 1000 else 800
            if not use_part_two:
                start_page = last_page if state == last_state and cause == last_causes else 1
            else:
                start_page = 1
            for page in range(start_page, pages + 1):
                sleep_time = randint(2, 7)
                try:
                    print(f"Scraping page {page} of {pages} for {cause} in {state}")
                    query = q_builder(cause, state, page=page)
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
                if not use_part_two:
                    last_cursor.state = state
                    last_cursor.cause = cause
                    last_cursor.page = page + 1
                    last_cursor.save()    
                sleep(sleep_time)
            notification.alert(
                Notify.info(
                    f"Finished scraping {cause} in {state}"
                )
            )
        notification.alert(
            Notify.info(
                f"Finished scraping {state}"
            )
        )
        deep_sleep = randint(100, 200)
        print(f"Deep sleeping for {deep_sleep} seconds")
        
    print("Finished scraping all data")             
    notification.alert(
        Notify.info(
            f"Finished scraping all data"
        )
    )
    return


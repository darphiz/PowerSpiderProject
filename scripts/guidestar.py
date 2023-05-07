import os
import re
from random import randint
from time import sleep
from guidestar_app.models import GuideStarIndexedUrl, ErrorPage, LastPage
from guidestar_app.v2_services import IndexGGUrls
from ngo_scraper.notification import Notify
from django.conf import settings
from django.db import IntegrityError
from scripts.utils import short_region_name

notification = Notify(settings.GUIDESTAR_HOOK or None)

def start_indexing(state, city="", no_cursor=False):
    last_cursor = None
    if not no_cursor:
        last_cursor = LastPage.objects.get_or_create(state=state, city=city)[0]
    
    try:
        max_cursor = IndexGGUrls(state, page=1, city=city).get_max_page(use_v2=bool(city)) 
    except Exception as e:
        print(f"Error getting max page for {state} {city}: {str(e)}")
        max_cursor = 50
        
    unique_urls_found = 0
    if last_cursor:
        print(f"Starting indexing {state} from page {last_cursor.page + 1} / {max_cursor} (city: {city})")
    start_from = last_cursor.page + 1 if last_cursor else 0
    
    for page in range(start_from, max_cursor):
        print(f"Indexing {state} page {page} / {max_cursor}")
        try:
            data = IndexGGUrls(state, page, city=city).scrape(use_v2=bool(city))
        except Exception as e:
            print(f"Error scraping {state} page {page}: {str(e)}")
            data = []
            ErrorPage.objects.update_or_create(
                state=state,
                page=page,
                city=city,
            )
        if not data:
            print("No data found. Skipping")
            continue
        
        # save data
        print(f"Saving {len(data)} urls for {state} page {page}")
        for ngo_data in data:
            try:
                GuideStarIndexedUrl.objects.create(**ngo_data)
                unique_urls_found += 1
            except IntegrityError:
                pass
            except Exception as e:
                print(f"Error saving {ngo_data['url']}: {str(e)}")
        if not no_cursor:
            last_cursor.page = page
            last_cursor.city = city
            last_cursor.save()
        sleep_time = randint(2, 5) 
        print(f"Found {unique_urls_found} unique url(s)")
        print(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time)

    notification.alert(f"Finished indexing {state}")
    print(f"Finished indexing {state}")
     
    
def index_urls(use_v2:bool=False):
    states = [  
            'Alaska',
            'Alabama',
            'Arkansas',
            'American Samoa',
            'Arizona',
            'California',
            'Colorado',
            'Connecticut',
            'District of Columbia',
            'Delaware',
            'Florida',
            'Georgia',
            'Guam',
            'Hawaii',
            'Iowa',
            'Idaho',
            'Illinois',
            'Indiana',
            'Kansas',
            'Kentucky',
            'Louisiana',
            'Massachusetts',
            'Maryland',
            'Maine',
            'Michigan',
            'Minnesota',
            'Missouri',
            'Northern Mariana Islands',
            'Mississippi',
            'Montana',
            'National',
            'North Carolina',
            'North Dakota',
            'Nebraska',
            'New Hampshire',
            'New Jersey',
            'New Mexico',
            'Nevada',
            'New York',
            'Ohio',
            'Oklahoma',
            'Oregon',
            'Pennsylvania',
            'Puerto Rico',
            'Rhode Island',
            'South Carolina',
            'South Dakota',
            'Tennessee',
            'Texas',
            'Utah',
            'Virginia',
            'Virgin Islands',
            'Vermont',
            'Washington',
            'Wisconsin',
            'West Virginia',
            'Wyoming'
              ]
    for state in states:
        if use_v2:
            state_abbr = short_region_name(state)
            cities = get_cities(state_abbr)
            print(f"Scraping {state} with {len(cities)} cities")
            for city in cities:
                start_indexing(state, city=city)
        else:       
            start_indexing(state)
        
        sleep_time = randint(100, 300)
        print(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time)
        
        

        
def get_cities(state_abbr):        
    file_path = f"scripts/guide_section/{state_abbr}.txt"
    cities = []
    if os.path.isfile(file_path):
        with open(file_path) as fp:
            city_list = fp.readlines()
        for city in city_list:
            cities.append(city.strip())
    return cities


def error_indexer(city, state, page):
    if not page:
        return True
    data = IndexGGUrls(state, page, city=city).scrape(use_v2=bool(city))
    if not data:
        print("No data found. Skipping")
        return True
    # save data
    print(f"Saving {len(data)} urls for {state} page {page}")
    unique_counter = 0
    for ngo_data in data:
        try:
            GuideStarIndexedUrl.objects.create(**ngo_data)
            unique_counter += 1
        except IntegrityError:
            print(f"Duplicate url found: {ngo_data['url']}")
        except Exception as e:
            print(f"Error saving {ngo_data['url']}: {str(e)}")
    print(f"Found {unique_counter} unique url(s)")
    print(f"Finished indexing {state} page {page}")
    sleep_time = randint(1,3)
    print(f"Sleeping for {sleep_time} seconds")
    sleep(sleep_time)
    return 


def re_crawl():
    for error in ErrorPage.objects.all():
        try:
            error_indexer(error.city, error.state, error.page)
            error.delete()
        except Exception as e:
            print(f"Error re-indexing {error.state} page {error.page}: {str(e)}")
        



def test():
    state = "Alabama"
    city = "AL - Birmingham"
    max_cursor = IndexGGUrls(state, page=1, city=city).get_max_page(use_v2=bool(city)) 
    print(max_cursor)
    
    
def extract_url(input_string):
    pattern = r'"(https?://.*?)"'
    return match.group(1) if (match := re.search(pattern, input_string)) else None
    
def stream_and_extract(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield extract_url(line)

def extract_path(url):
    if not url:
        print("No url found")
        return None
    domain = "guidestar.org"
    index = url.find(domain)
    if index != -1:
        return url[index + len(domain):]
    else:
        return None
    
def load_urls():        
    counter = 0        
    for url in stream_and_extract('gs_urls.txt'):
        g_url = extract_path(url)
        if not g_url:
            continue
        try:
            GuideStarIndexedUrl.objects.create(url=g_url)
            counter += 1
            print(f"Saved {url}")
        except IntegrityError:
            print(f"Duplicate url found: {g_url} -> SKIPPED")
        except Exception as e:
            print(f"Error saving {g_url}: {str(e)}")
    print(f"Saved {counter} new urls")
    return
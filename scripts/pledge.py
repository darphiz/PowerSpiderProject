from pledge_app.services import PledgeListCrawler
from pledge_app.models import LastPage, PledgeIndexedUrl
from time import sleep
from random import randint
from django.db import IntegrityError
from .utils import sub_causes


def save_links(links:list):
    try:
        PledgeIndexedUrl.objects.bulk_create(
            [PledgeIndexedUrl(url=link) for link in links],
            ignore_conflicts=True
        )
    except IntegrityError as e:
        print(f"Error saving links: {str(e)}")
    except Exception as e:
        print(f"Error saving links: {str(e)}")
        
    return
    

def index_pledge_link(sub_causes_only:bool=False):
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
        'OK',
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
    causes = ["animals", 
              "art", 
              "disaster-relief", 
              "education", 
              "environment",
              "health",
              "justice",
              "science",
              "society"
            ]
    
    # last_cursor = LastPage.objects.first()
    # if not last_cursor:
    #     last_cursor = LastPage.objects.create(state=states[0], cause=causes[0], page=0)
    
    # last_state = last_cursor.state
    # last_causes = last_cursor.cause
    # last_page = last_cursor.page
    # states = states[states.index(last_state):]
    # causes = causes[causes.index(last_causes):]
    
    # print(f"Starting from {last_state} page {last_page} on {last_causes}")
    
    if sub_causes_only:
        states = ["", ]
        causes = sub_causes
    
    for state in states:
        for cause in causes:
            print(f"Indexing {state} on {cause}")
            max_page = PledgeListCrawler(state=state, cause=cause).get_max_result()
            max_page = int(max_page/12) 
            max_page = max_page if max_page < 800 else 800
            print(f"Maximum possible page for {cause} in {state} is {max_page} pages")
            chunks = 5
            start_page = 0
            for i in range(start_page, max_page, chunks):
                start = i+1
                stop = i + chunks
                crawler = PledgeListCrawler(start=start, end=stop, state=state, cause=cause)
                all_links = crawler.crawl_all()
                
                print(f"Saving {len(all_links)} links for {state} page {start} to {stop} on {cause}")
                #save Links here
                save_links(all_links)        
                # update last cursor
                # last_cursor.state = state
                # last_cursor.cause = cause
                # last_cursor.page = stop
                # last_cursor.save()
                
                sleep_time = randint(3, 6)
                print(f"Sleeping for {sleep_time} seconds")
                sleep(sleep_time)
                
                




#matches
# pure cause done
# pure sub cause started
# pure state
# pure country
# pure sub cause and state
# country and cause done

from pledge_app.services import PledgeListCrawler
from pledge_app.models import PledgeIndexedUrl
from time import sleep
from random import randint
from django.db import IntegrityError
from .pledge_data import pledge_causes,pledge_states, pledge_countries           

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
           

def index_cause_state():
    causes = pledge_causes
    states = pledge_states
    for state in states:
        for cause in causes:
            print(f"Indexing {state} on {cause}")
            max_page = PledgeListCrawler(state=state, cause=cause).get_max_result()
            max_page = int(max_page/12) 
            max_page = max_page if max_page <= 1000 else 1000
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
                
                sleep_time = randint(2, 5)
                print(f"Sleeping for {sleep_time} seconds")
                sleep(sleep_time)

def index_cause_country():
    causes = pledge_causes
    countries = pledge_countries
    for country in countries:
        for cause in causes:
            print(f"Indexing {country} on {cause}")
            max_page = PledgeListCrawler(country=country, cause=cause).get_max_result()
            max_page = int(max_page/12) 
            max_page = max_page if max_page <= 1000 else 1000
            print(f"Maximum possible page for {cause} in {country} is {max_page} pages")
            chunks = 5
            start_page = 0
            for i in range(start_page, max_page, chunks):
                start = i+1
                stop = i + chunks
                crawler = PledgeListCrawler(start=start, end=stop, country=country, cause=cause)
                all_links = crawler.crawl_all()
                
                print(f"Saving {len(all_links)} links for {country} page {start} to {stop} on {cause}")
                #save Links here
                save_links(all_links)        
                
                sleep_time = randint(2, 5)
                print(f"Sleeping for {sleep_time} seconds")
                sleep(sleep_time)

def index_state_country():
    states = pledge_states
    countries = ["US", ]
    for country in countries:
        for state in states:
            print(f"Indexing {country} on {state}")
            max_page = PledgeListCrawler(country=country, state=state).get_max_result()
            max_page = int(max_page/12) 
            max_page = max_page if max_page <= 1000 else 1000
            print(f"Maximum possible page for {state} in {country} is {max_page} pages")
            chunks = 5
            start_page = 0
            for i in range(start_page, max_page, chunks):
                start = i+1
                stop = i + chunks
                crawler = PledgeListCrawler(start=start, end=stop, country=country, state=state)
                all_links = crawler.crawl_all()
                
                print(f"Saving {len(all_links)} links for {country} page {start} to {stop} on {state}")
                #save Links here
                save_links(all_links)        
                
                sleep_time = randint(2, 5)
                print(f"Sleeping for {sleep_time} seconds")
                sleep(sleep_time)
                
                
def index_cause_state_country():
    causes = pledge_causes
    states = pledge_states
    countries = ["US",]
    for country in countries:
        for state in states:
            for cause in causes:
                print(f"Indexing {country} on {state} on {cause}")
                max_page = PledgeListCrawler(country=country, state=state, cause=cause).get_max_result()
                max_page = int(max_page/12) 
                max_page = max_page if max_page <= 1000 else 1000
                print(f"Maximum possible page for {cause} in {state} in {country} is {max_page} pages")
                chunks = 5
                start_page = 0
                for i in range(start_page, max_page, chunks):
                    start = i+1
                    stop = i + chunks
                    crawler = PledgeListCrawler(start=start, end=stop, country=country, state=state, cause=cause)
                    all_links = crawler.crawl_all()
                    
                    print(f"Saving {len(all_links)} links for {country} page {start} to {stop} on {state} on {cause}")
                    #save Links here
                    save_links(all_links)        
                    
                    sleep_time = randint(1, 3)
                    print(f"Sleeping for {sleep_time} seconds")
                    sleep(sleep_time)
    print("Done")
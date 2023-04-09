from pledge_app.services import PledgeListCrawler
from pledge_app.models import LastPage, PledgeIndexedUrl
from time import sleep
from random import randint
from django.db import IntegrityError

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
    
"""
To do a country combo search, use the following:
note: Variable "states" is a lists of all countries in the world
"""
def index_pledge_link(use_country_only:bool=False):
    states = [
        "AF",
        "AL",
        "DZ",
        "AD",
        "AO",
        "AG",
        "AR",
        "AM",
        "AU",
        "AT",
        "AZ",
        "BS",
        "BH",
        "BD",
        "BB",
        "BY",
        "BE",
        "BZ",
        "BJ",
        "BT",
        "BO",
        "BA",
        "BW",
        "BR",
        "BN",
        "BG",
        "BF",
        "BI",
        "KH",
        "CM",
        "CA",
        "CV",
        "CF",
        "TD",
        "CL",
        "CN",
        "CO",
        "KM",
        "CG",
        "CD",
        "CR",
        "CI",
        "HR",
        "CU",
        "CY",
        "CZ",
        "DK",
        "DJ",
        "DM",
        "DO",
        "EC",
        "EG",
        "SV",
        "GQ",
        "ER",
        "EE",
        "ET",
        "FJ",
        "FI",
        "FR",
        "GA",
        "GM",
        "GE",
        "DE",
        "GH",
        "GR",
        "GD",
        "GT",
        "GN",
        "GW",
        "GY",
        "HT",
        "HN",
        "HU",
        "IS",
        "IN",
        "ID",
        "IR",
        "IQ",
        "IE",
        "IL",
        "IT",
        "JM",
        "JP",
        "JO",
        "KZ",
        "KE",
        "KI",
        "KP",
        "KR",
        "KW",
        "KG",
        "LA",
        "LV",
        "LB",
        "LS",
        "LR",
        "LY",
        "LI",
        "LT",
        "LU",
        "MG",
        "MW",
        "MY",
        "MV",
        "ML",
        "MT",
        "MH",
        "MR",
        "MU",
        "MX",
        "FM",
        "MD",
        "MC",
        "MN",
        "ME",
        "MA",
        "MZ",
        "MM",
        "NA",
        "NR",
        "NP",
        "NL",
        "NZ",
        "NI",
        "NE",
        "NG",
        "MK",
        "NO",
        "OM",
        "PK",
        "PW",
        "PA",
        "PG",
        "PY",
        "PE",
        "PH",
        "PL",
        "PT",
        "QA",
        "RO",
        "RU",
        "RW",
        "KN",
        "LC",
        "VC",
        "WS",
        "SM",
        "ST",
        "SA",
        "SN",
        "RS",
        "SC",
        "SL",
        "SG",
        "SK",
        "SI",
        "SB",
        "SO",
        "ZA",
        "ES",
        "LK",
        "SD",
        "SR",
        "SZ",
        "SE",
        "CH",
        "SY",
        "TW",
        "TJ",
        "TZ",
        "TH",
        "TL",
        "TG",
        "TO",
        "TT",
        "TN",
        "TR",
        "TM",
        "TV",
        "UG",
        "UA",
        "AE",
        "GB",
        "US",
        "UY",
        "UZ",
        "VU",
        "VA",
        "VE",
        "VN",
        "YE",
        "ZM",
        "ZW"
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
    
    
    if use_country_only:
        causes = ["",]
    
    for state in states:
        for cause in causes:
            print(f"Indexing {state} on {cause}")
            max_page = PledgeListCrawler(country=state, cause=cause).get_max_result()
            max_page = int(max_page/12) 
            max_page = max_page if max_page <= 1000 else 1000
            print(f"Maximum possible page for {cause} in {state} is {max_page} pages")
            chunks = 5
            start_page = 0
            for i in range(start_page, max_page, chunks):
                start = i+1
                stop = i + chunks
                crawler = PledgeListCrawler(start=start, end=stop, country=state, cause=cause)
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
                
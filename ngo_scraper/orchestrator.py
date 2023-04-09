SCRAPER_Q = {
    # scrape indexed pledge urls
    'start_scraping_pledge': {
        'task' : 'start_scraping',
        'schedule' : 15.0,
    },
       
    # Scraper to scrape data from global_giving website
    # "gg_url_crawler": {
    #     "task": "start_scraping_gg",
    #     "schedule": 12.0,
    # },
    
    # FCRA scraper
    # "fcr_data_spider": {
    #     "task": "start_scraping_fcr",
    #     "schedule": 20.0,
    # },
    
    
    # scrape guide star indexed urls
    "start_scraping_guidestar" : {
        "task": "start_scraping_guidestar",
        "schedule": 18.0,
    },
    
    # scrape indexed urls from irs
    # "start_scraping_irs" : {
    #     "task": "start_scraping_irs",
    #     "schedule": 13.0,
    # },
    
    
    # scrape indexed urls from guide star india
    "start_scraping_ggi" : {
        "task": "start_scraping_ggi",
        "schedule": 300.0,
    }
    
    # download xml file from irs
    # "download_xml_file" : {
    #     "task": "index_irs_xml_url",
    #     "schedule": 120.0,
    # }   
}


SPIDERS_Q = {
    ###### PLEDGE.TO spider
    # "pledge_url_crawler": {
    #     'task': 'crawl_pledge',
    #     'schedule' : 20.0,
    # },
    
    #  CHARITY navigator spider
    # "start_scraping_charity" : {
    #     "task": "start_scraping_charity",
    #     "schedule": 8.0,
    # },
    
    # Charity Navigator Retry Spider
    # "charity_retry_failed_pages" : {
    #     "task": "charity_retry_failed_pages",
    #     "schedule": 25.0,
    # },
    
    # index guide star urls
    # "index_guidestar_url" : {
    #     "task": "index_guidestar_url",
    #     "schedule": 20.0,
    # }   ,
}





MONITORING_Q = {
    
    # PLEDGE.TO monitoring
    # "report_pledge": {
    #     'task': 'report_pledge',
    #     'schedule' : 300.0,
    #     'options': {'queue': 'report'}
    # },
}


all_tasks = {**SCRAPER_Q, **SPIDERS_Q, **MONITORING_Q}
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ngo_scraper.settings')
app = Celery('ngo_scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


SCRAPER_Q = {
    # scrape indexed pledge urls
    # 'start_scraping_pledge': {
    #     'task' : 'start_scraping',
    #     'schedule' : 25.0,
    # },
       
    # Scraper to scrape data from global_giving website
    # "gg_url_crawler": {
    #     "task": "start_scraping_gg",
    #     "schedule": 40.0,
    # }
    
    # FCRA scraper
    # "fcr_data_spider": {
    #     "task": "start_scraping_fcr",
    #     "schedule": 20.0,
    # }
    
    # index guide star urls
    # "index_guidestar_url" : {
    #     "task": "index_guidestar_url",
    #     "schedule": 60.0,
    # }   ,
    
    # scrape guide star indexed urls
    # "start_scraping_guidestar" : {
    #     "task": "start_scraping_guidestar",
    #     "schedule": 120.0,
    # },
    
    # scrape indexed urls from irs
    # "start_scraping_irs" : {
    #     "task": "start_scraping_irs",
    #     "schedule": 80.0,
    # }   
    
    
    # scrape indexed urls from guide star india
    "start_scraping_ggi" : {
        "task": "start_scraping_ggi",
        "schedule": 20.0,
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
    #     "schedule": 20.0,
    # },
    
    # Charity Navigator Retry Spider
    # "charity_retry_failed_pages" : {
    #     "task": "charity_retry_failed_pages",
    #     "schedule": 25.0,
    # },
}





MONITORING_Q = {
    
    # PLEDGE.TO monitoring
    # "report_pledge": {
    #     'task': 'report_pledge',
    #     'schedule' : 300.0,
    #     'options': {'queue': 'report'}
    # },
}


app.conf.beat_schedule = SCRAPER_Q | SPIDERS_Q | MONITORING_Q
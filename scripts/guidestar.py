from random import randint
from contextlib import suppress
from time import sleep
from guidestar_app.models import GuideStarIndexedUrl, ErrorPage, LastPage
from guidestar_app.v2_services import IndexGGUrls
from ngo_scraper.notification import Notify
from django.conf import settings

notification = Notify(settings.GUIDESTAR_HOOK or None)

def start_indexing(state, max_cursor = 400):
    last_cursor = LastPage.objects.get_or_create(state=state)[0]
    for page in range(last_cursor.page + 1, max_cursor):
        print(f"Indexing {state} page {page} / {max_cursor}")
        data = IndexGGUrls(state, page).scrape()
        if not data:
            ErrorPage.objects.update_or_create(
                state=state,
                page=page,
            )
            continue
        
        # save data
        print(f"Saving {len(data)} urls for {state} page {page}")
        for ngo_data in data:
            try:
                GuideStarIndexedUrl.objects.create(**ngo_data)
            except Exception as e:
                print(f"Error saving {ngo_data['url']}: {str(e)}")
        
        last_cursor.page = page
        last_cursor.save()
        sleep_time = randint(20, 30) 
        print(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time)
    
    notification.alert(f"Finished indexing {state}")
    print(f"Finished indexing {state}")
    
    
    
def index_many_states():
    states = ["Alabama", "Arkansas", "American Samoa", "Arizona", "California"]
    for state in states:
        start_indexing(state)
        sleep_time = randint(300, 600)
        print(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time)
        
        
        
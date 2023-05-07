import re
from global_giving.models import NGO
from global_giving.services import GlobalGivingScraper

def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)


def get_duplicates():
    duplicates = []
    all_ngos = NGO.objects.all()
    total = all_ngos.count()
    counter = 0
    for ngo in all_ngos:
        ngo_name = ngo.organization_name
        ngo_urls_scraped = ngo.urls_scraped
        has_duplicates = NGO.objects.filter(organization_name=ngo_name, urls_scraped= ngo_urls_scraped).count() > 1
        if has_duplicates:
            print(f"Duplicate found: {ngo_name}")
            duplicates.append(ngo.id)
        counter += 1
        print(f"{counter} of {total} done")
    unique_duplicates = set(duplicates)
    return unique_duplicates




def delete_duplicates(ids: list):
    for id in ids:
        try:
            ngo = NGO.objects.get(id=id)
        except NGO.DoesNotExist:
            print(f"NGO with id {id} does not exist")
            continue
        similar_ngos = NGO.objects.filter(organization_name=ngo.organization_name, urls_scraped=ngo.urls_scraped)
        if similar_ngos.count() > 1:
            print(f"Deleting {ngo.organization_name}")
            similar_ngos.exclude(id=ngo.id).delete()
    print("Done")
    
    
def missing_website():
    ngos = NGO.objects.filter(website="")
    return ngos    
    
def missing_cause():
    ngos = NGO.objects.filter(cause__isnull=True)
    return ngos
def missing_reg_year():
    ngos = NGO.objects.filter(registration_date_year__isnull=True)
    return ngos
def missing_mission():
    ngos = NGO.objects.filter(mission__isnull=True)
    return ngos

def to_rescrape():
    n_with_missing_website = missing_website()
    n_with_missing_cause = missing_cause()
    n_with_missing_reg_year = missing_reg_year()
    n_with_missing_mission = missing_mission()
    return n_with_missing_website | n_with_missing_cause | n_with_missing_reg_year | n_with_missing_mission


def start_scraping():
    """
    start updating NGO with missing fields
    only update if the field is None or ""
    """
    ngo_with_missing_fields = to_rescrape()
    total = ngo_with_missing_fields.count()
    counter = 0
    for ngo in ngo_with_missing_fields:
        
        try:
            spider = GlobalGivingScraper()
            url = reverse_list(ngo.urls_scraped)[0]
            data = spider.scrape(url, scrape_images=False)
            if not data:
                print(f"Error scraping {ngo.organization_name}: No data")
                continue
            if data["website"] and ngo.website == "":
                ngo.website = data["website"]
            if data["cause"] and ngo.cause is None:
                ngo.cause = data["cause"]
            if data["registration_date_year"] and ngo.registration_date_year is None:
                ngo.registration_date_year = data["registration_date_year"]
            if data["mission"] and ngo.mission is None:
                ngo.mission = data["mission"]
            ngo.save()
        except Exception as e:
            print(f"Error scraping {ngo.organization_name}: {e}")
        counter += 1
        print(f"{counter} of {total} done")
        
    print("Done")
    
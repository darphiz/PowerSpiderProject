from contextlib import suppress
from merger.models import UniqueNGO
from pledge_app.models import NGO
from django.core.paginator import Paginator


def get_ein(string):
    with suppress(Exception):
        if not string:
            return None
        ein_start = string.find('organizations/') + 14
        ein_end = string.find('/', ein_start)
        ein = string[ein_start:ein_end].replace('-', '')  # Remove hyphen before converting to int
        return ein  
    return None



def merge_pledge():
    all_fcra_ngos = NGO.objects.all()        
    total = all_fcra_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=get_ein(ngo.urls_scraped),
            govt_reg_number_type="ein",
            pledge_id = ngo.id,
        ) for ngo in all_fcra_ngos if get_ein(ngo.urls_scraped)
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total

def clean(ngos):
    total = ngos.count()
    counter = 0
    for ngo in ngos:
        ngo.govt_reg_number = get_ein(ngo.urls_scraped)
        ngo.save()
        counter += 1
        print(f"Cleaned {counter} of {total}")
    return total

def clean_pledge(page_num=1):
    all_pledge_ngos = NGO.objects.filter(govt_reg_number__isnull=True).order_by('id')
    total = all_pledge_ngos.count()
    hundred_thousand = Paginator(all_pledge_ngos, 100000)
    page_of_ngos = hundred_thousand.page(page_num)
    ngos = page_of_ngos.object_list
    clean(ngos)
    return total



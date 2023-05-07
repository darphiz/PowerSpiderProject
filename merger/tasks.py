from contextlib import suppress
from .models import UniqueNGO
from .scripts.merge_v2 import Merge
from celery import shared_task


@shared_task(name="merge_worker")
def merge_worker(ein):
    merger = Merge(ein)
    data = merger.merge_data()
    ngo_ = UniqueNGO.objects.get(govt_reg_number=ein)
    ngo_.has_merged = True
    with suppress(Exception):
        ngo_.organization_name = data['organization_name']
    with suppress(Exception):
        ngo_.organization_address = data['organization_address']
    with suppress(Exception):
        ngo_.country = data['country']
    with suppress(Exception):
        ngo_.state = data['state']
    with suppress(Exception):
        ngo_.cause= data['cause']
    with suppress(Exception):
        ngo_.email = data['email']
    with suppress(Exception):
        ngo_.phone = data['phone']
    with suppress(Exception):
        ngo_.mission = data['mission']
    with suppress(Exception):
        ngo_.description = data['description']
    with suppress(Exception):
        ngo_.registration_date_year = data['registration_date_year']
    with suppress(Exception):
        ngo_.registration_date_month = data['registration_date_month']
    with suppress(Exception):
        ngo_.registration_date_day = data['registration_date_day']
    with suppress(Exception):
        ngo_.gross_income = data['gross_income']
    with suppress(Exception):
        ngo_.govt_reg_number = data['govt_reg_number']
    with suppress(Exception):
        ngo_.govt_reg_number_type = data['govt_reg_number_type']   
    with suppress(Exception):
        ngo_.website = data['website']
    with suppress(Exception):
        ngo_.domain = data['domain']
    with suppress(Exception):
        ngo_.image = data['image']
    with suppress(Exception):
        ngo_.urls_scraped = data['urls_scraped']    
    ngo_.save()
    
    return
    
@shared_task(name="merger_orchestrator")
def merger_orchestrator():
    first_sixty = UniqueNGO.objects.filter(has_merged=False, locked=False)[:50]
    for ngo in first_sixty:
        ngo.locked = True
        ngo.save()
        merge_worker.delay(ngo.govt_reg_number)
    return



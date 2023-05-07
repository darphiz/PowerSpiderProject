from contextlib import suppress
from irs_app.models import NGO_V2
from merger.models import UniqueNGO

def merge_xml():
    all_xml_ngos = NGO_V2.objects.all()
    total = all_xml_ngos.count()
    print(f"Total: {total}")
    bulk_NGOs = [
        UniqueNGO(
            govt_reg_number=ngo.govt_reg_number,
            govt_reg_number_type="ein",
        ) for ngo in all_xml_ngos if ngo.govt_reg_number
    ]
    UniqueNGO.objects.bulk_create(bulk_NGOs, ignore_conflicts=True, batch_size=1000)
    print(f"Created {total} UniqueNGOs")
    return total




def special_case_org_name(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_org_names = all_eins.exclude(organization_name__isnull=True).exclude(organization_name__exact='')
            order_by_most_recent_domain = non_empty_org_names.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None    
    
def special_case_org_address(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_org_addresses = all_eins.exclude(organization_address__isnull=True).exclude(organization_address__exact='')
            order_by_most_recent_domain = non_empty_org_addresses.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_country(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_countries = all_eins.exclude(country__isnull=True).exclude(country__exact='')
            order_by_most_recent_domain = non_empty_countries.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_state(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_states = all_eins.exclude(state__isnull=True).exclude(state__exact='')
            order_by_most_recent_domain = non_empty_states.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_cause(ein, all_eins):
    with suppress(Exception):
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_causes = all_eins.exclude(cause__isnull=True).exclude(cause__exact='')
            order_by_most_recent_domain = non_empty_causes.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None


def special_case_email(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_emails = all_eins.exclude(email__isnull=True).exclude(email__exact='')
            order_by_most_recent_domain = non_empty_emails.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_phone(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_phones = all_eins.exclude(phone__isnull=True).exclude(phone__exact='')
            order_by_most_recent_domain = non_empty_phones.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_website(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_websites = all_eins.exclude(website__isnull=True).exclude(website__exact='')
            order_by_most_recent_domain = non_empty_websites.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_mission(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 0:
            return None
        if total == 1:
            return all_eins.first()
        else:
            non_empty_missions = all_eins.exclude(mission__isnull=True).exclude(mission__exact='')
            order_by_most_recent_domain = non_empty_missions.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_description(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 1:
            return all_eins.first()
        else:
            non_empty_descriptions = all_eins.exclude(description__isnull=True).exclude(description__exact='')
            order_by_most_recent_domain = non_empty_descriptions.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_registration_date_year(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 1:
            return all_eins.first()
        else:
            non_empty_registration_date_years = all_eins.exclude(registration_date_year__isnull=True).exclude(registration_date_year__exact='')
            order_by_most_recent_domain = non_empty_registration_date_years.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None

def special_case_gross_income(ein, all_eins):
    with suppress(Exception):
        
        total = all_eins.count()
        if total == 1:
            return all_eins.first()
        else:
            non_empty_gross_incomes = all_eins.exclude(gross_income__isnull=True).exclude(gross_income__exact='')
            order_by_most_recent_domain = non_empty_gross_incomes.order_by('-domain')
            return order_by_most_recent_domain.first()
    return None


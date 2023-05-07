from merger.scripts.irs_xml import special_case_cause, special_case_country, special_case_description, special_case_email, special_case_gross_income, special_case_mission, special_case_org_address, special_case_org_name, special_case_phone, special_case_registration_date_year, special_case_state, special_case_website
from pledge_app.models import NGO as PledgeNGO
from irs_app.models import NGO_V2 as IrsXML_NGO
from irs_app.models import ZIP_NGO as IrsZIP_NGO
from guidestar_app.models import NGO as GuidestarNGO
from c_navigator.models import NGO as CharityNavigatorNGO
from fcra_app.models import FCR_NGO
from global_giving.models import NGO as GlobalGivingNGO
from global_giving_india.models import NGO as GuideStarIndiaNGO
import re

def reverse_list(string):
    return re.findall(r'"([^"]*)"', string)

def format_list(lists):
    try:
        if not lists:
            return None
        if not isinstance(lists, list):
            lists = [lists]
        _set = {"\"" + x + "\"" for x in lists}
        _set = str(_set).replace("'", "")
        return _set
    except Exception:
        return None



def merge_all_fields(ein:str):
    domain_list = []
    urls_scraped_list = []
    
    organization_name = get_organization_name(ein, domain_list, urls_scraped_list)
    organization_address = get_organization_address(ein, domain_list, urls_scraped_list)
    country = get_country(ein, domain_list, urls_scraped_list)   
    state = get_state(ein, domain_list, urls_scraped_list)
    cause = get_cause(ein, domain_list, urls_scraped_list)
    email = get_email(ein, domain_list, urls_scraped_list)
    phone = get_phone(ein, domain_list, urls_scraped_list)
    website = get_website(ein, domain_list, urls_scraped_list)
    mission = get_mission(ein, domain_list, urls_scraped_list)
    description = get_description(ein, domain_list, urls_scraped_list)
    registration_date_year = get_registration_date_year(ein, domain_list, urls_scraped_list)
    registration_date_month = get_registration_date_month(ein, domain_list, urls_scraped_list)
    registration_date_day = get_registration_date_day(ein, domain_list, urls_scraped_list)
    gross_income = get_gross_income(ein, domain_list, urls_scraped_list)
    image = get_image(ein, domain_list, urls_scraped_list)
    return {
        "organization_name": organization_name,
        "organization_address": organization_address,
        "country": country,
        "state": state,
        "cause": cause,
        "email": email,
        "phone": phone,
        "website": website,
        "mission": mission,
        "description": description,
        "registration_date_year": registration_date_year,
        "registration_date_month": registration_date_month,
        "registration_date_day": registration_date_day,
        "gross_income": gross_income,
        "image": image,
        "domain" : merge_list(domain_list),
        "urls_scraped" : merge_list(urls_scraped_list),
        "has_merged": True,
    }


def merge_list(domain_list:list):
    valid_domain_list = []
    if len(domain_list) == 0:
        return None
    for domain in domain_list:
        rev_list = reverse_list(domain)
        for rev in rev_list:
            valid_domain_list.append(rev)
    unique_domain_list = list(set(valid_domain_list))
    return format_list(unique_domain_list)



def get_image(ein, domain_list, urls_scraped_list):
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.image:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.image
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.image:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.image
    in_guidestar_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar_india:
        if in_guidestar_india.image:
            domain_list.append(in_guidestar_india.domain)
            urls_scraped_list.append(in_guidestar_india.urls_scraped)
            return in_guidestar_india.image
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.image:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.image
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.image:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.image
    return None
        




def get_gross_income(ein, domain_list, urls_scraped_list):
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.gross_income:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.gross_income
    in_irs_xml = special_case_gross_income(ein)
    if in_irs_xml:
        if in_irs_xml.gross_income:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.gross_income
    in_guidestar_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar_india:
        if in_guidestar_india.gross_income:
            domain_list.append(in_guidestar_india.domain)
            urls_scraped_list.append(in_guidestar_india.urls_scraped)
            return in_guidestar_india.gross_income
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.gross_income:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.gross_income
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.gross_income:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.gross_income
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.gross_income:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.gross_income
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.gross_income:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.gross_income
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.gross_income:
            return in_pledge.gross_income
    return None
    
    
def get_registration_date_day(ein, domain_list, urls_scraped_list):
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.registration_date_day:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.registration_date_day
    return None

def get_registration_date_month(ein, domain_list, urls_scraped_list):
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.registration_date_month:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.registration_date_month
    return None

def get_registration_date_year(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.registration_date_year:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.registration_date_year
    in_guidestar_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar_india:
        if in_guidestar_india.registration_date_year:
            domain_list.append(in_guidestar_india.domain)
            urls_scraped_list.append(in_guidestar_india.urls_scraped)
            return in_guidestar_india.registration_date_year
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.registration_date_year:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.registration_date_year
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.registration_date_year:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.registration_date_year
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.registration_date_year:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.registration_date_year
    in_irs_xml = special_case_registration_date_year(ein)
    if in_irs_xml:
        if in_irs_xml.registration_date_year:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.registration_date_year
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.registration_date_year:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.registration_date_year
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.registration_date_year:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.registration_date_year
    return None

def get_description(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.description:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.description
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.description:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.description
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.description:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.description
    in_irs_xml = special_case_description(ein)
    if in_irs_xml:
        if in_irs_xml.description:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.description
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.description:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.description
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.description:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.description
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.description:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.description
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.description:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.description
    return None
    

def get_mission(ein, domain_list, urls_scraped_list):    
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.mission:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)    
            return in_pledge.mission
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.mission:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.mission
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.mission:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.mission
    in_irs_xml = special_case_mission(ein)
    if in_irs_xml:
        if in_irs_xml.mission:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.mission
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.mission:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.mission
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.mission:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.mission
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.mission:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.mission
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.mission:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.mission
    return None
    
def get_website(ein, domain_list, urls_scraped_list):
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.website:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.website
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.website:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.website
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.website:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.website
    in_irs_xml = special_case_website(ein)
    if in_irs_xml:
        if in_irs_xml.website:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.website
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.website:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.website
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.website:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.website
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.website:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.website
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra: 
        if in_fcra.website:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.website
    return None    
    
def get_phone(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.phone:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.phone
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.phone:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.phone
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.phone:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.phone
        
    in_charity_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_charity_navigator:
        if in_charity_navigator.phone:
            domain_list.append(in_charity_navigator.domain)
            urls_scraped_list.append(in_charity_navigator.urls_scraped)
            return in_charity_navigator.phone
    in_irs_xml = special_case_phone(ein)
    if in_irs_xml:
        if in_irs_xml.phone:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.phone
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.phone:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.phone
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.phone:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.phone
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra: 
        if in_fcra.phone:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.phone
    
def get_email(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.email:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.email
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.email:
            domain_list.append(in_c_navigator.domain)
            urls_scraped_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.email
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.email:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.email
    in_irs_xml = special_case_email(ein)
    if in_irs_xml:
        if in_irs_xml.email:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.email
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.email:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.email
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.email:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.email
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.email:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.email
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.email:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.email
    return None
    
def get_cause(ein, domain_list, urls_scraped_list):
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.cause:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.cause
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.cause:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.cause
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.cause:
            domain_list.append(in_c_navigator.domain)
            urls_scraped_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.cause
    in_irs_xml = special_case_cause(ein)
    if in_irs_xml:
        if in_irs_xml.cause:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.cause
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.cause:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.cause
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.cause:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.cause
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.cause:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.cause
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.cause:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.cause
    return None
    
def get_state(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.state:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.state
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.state:
            domain_list.append(in_c_navigator.domain)
            urls_scraped_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.state
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.state:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.state
    in_irs_xml = special_case_state(ein)
    if in_irs_xml:
        if in_irs_xml.state:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.state
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.state:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.state
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.state:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.state
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.state:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.state
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.state:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.state
    in_irs_xml = IrsXML_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_xml:
        if in_irs_xml:
            if in_irs_xml.state:
                domain_list.append(in_irs_xml.domain)
                urls_scraped_list.append(in_irs_xml.urls_scraped)
                return in_irs_xml.state
    return None
    
def get_country(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.country:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.country
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.country:
            domain_list.append(in_c_navigator.domain)
            urls_scraped_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.country
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.country:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.country
    in_irs_xml = special_case_country(ein)
    if in_irs_xml:
        if in_irs_xml.country:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.country
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.country:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.country
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.country:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.country
    in_guide_star_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guide_star_india:
        if in_guide_star_india.country:
            domain_list.append(in_guide_star_india.domain)
            urls_scraped_list.append(in_guide_star_india.urls_scraped)
            return in_guide_star_india.country
    in_frca = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_frca:
        if in_frca.country:
            domain_list.append(in_frca.domain)
            urls_scraped_list.append(in_frca.urls_scraped)
            return in_frca.country
    
    return None

def get_organization_address(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.organization_address:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.organization_address
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.organization_address:
            domain_list.append(in_c_navigator.domain)
            urls_scraped_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.organization_address
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.organization_address:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.organization_address
    in_irs_xml = special_case_org_address(ein)
    if in_irs_xml:
        if in_irs_xml.organization_address:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.organization_address
    
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.organization_address:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.organization_address
    
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.organization_address:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.organization_address
    in_guidestar_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar_india:
        if in_guidestar_india.organization_address:
            domain_list.append(in_guidestar_india.domain)
            urls_scraped_list.append(in_guidestar_india.urls_scraped)
            return in_guidestar_india.organization_address
    
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.organization_address:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.organization_address
    return None        
    


def get_organization_name(ein, domain_list, urls_scraped_list):
    in_guidestar = GuidestarNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar:
        if in_guidestar.organization_name:
            domain_list.append(in_guidestar.domain)
            urls_scraped_list.append(in_guidestar.urls_scraped)
            return in_guidestar.organization_name
    in_c_navigator = CharityNavigatorNGO.objects.filter(govt_reg_number=ein).first()
    if in_c_navigator:
        if in_c_navigator.organization_name:
            domain_list.append(in_c_navigator.domain)
            domain_list.append(in_c_navigator.urls_scraped)
            return in_c_navigator.organization_name
    in_pledge = PledgeNGO.objects.filter(govt_reg_number=ein).first()
    if in_pledge:
        if in_pledge.organization_name:
            domain_list.append(in_pledge.domain)
            urls_scraped_list.append(in_pledge.urls_scraped)
            return in_pledge.organization_name
    in_irs_xml = special_case_org_name(ein)
    if in_irs_xml:
        if in_irs_xml.organization_name:
            domain_list.append(in_irs_xml.domain)
            urls_scraped_list.append(in_irs_xml.urls_scraped)
            return in_irs_xml.organization_name
    in_irs_zip = IrsZIP_NGO.objects.filter(govt_reg_number=ein).first()
    if in_irs_zip:
        if in_irs_zip.organization_name:
            domain_list.append(in_irs_zip.domain)
            urls_scraped_list.append(in_irs_zip.urls_scraped)
            return in_irs_zip.organization_name
    in_global_giving = GlobalGivingNGO.objects.filter(govt_reg_number=ein).first()
    if in_global_giving:
        if in_global_giving.organization_name:
            domain_list.append(in_global_giving.domain)
            urls_scraped_list.append(in_global_giving.urls_scraped)
            return in_global_giving.organization_name
    in_guidestar_india = GuideStarIndiaNGO.objects.filter(govt_reg_number=ein).first()
    if in_guidestar_india:
        if in_guidestar_india.organization_name:
            domain_list.append(in_guidestar_india.domain)
            urls_scraped_list.append(in_guidestar_india.urls_scraped)
            return in_guidestar_india.organization_name
    in_fcra = FCR_NGO.objects.filter(govt_reg_number=ein).first()
    if in_fcra:
        if in_fcra.organization_name:
            domain_list.append(in_fcra.domain)
            urls_scraped_list.append(in_fcra.urls_scraped)
            return in_fcra.organization_name
    return None


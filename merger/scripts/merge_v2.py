from contextlib import suppress
from merger.scripts.irs_xml import special_case_cause, special_case_country, special_case_description, special_case_email, special_case_gross_income, special_case_mission, special_case_org_address, special_case_org_name, special_case_phone, special_case_registration_date_year, special_case_state, special_case_website
from pledge_app.models import NGO as PledgeNGO
from irs_app.models import NGO_V2 as IrsXML_NGO
from irs_app.models import ZIP_NGO as IrsZIP_NGO
from guidestar_app.models import NGO as GuidestarNGO
from c_navigator.models import NGO as CharityNavigatorNGO
from fcra_app.models import FCR_NGO
from global_giving_india.models import NGO as GuideStarIndiaNGO
import re
from time import time


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


class Merge:
    def __init__(self, ein) -> None:
        self.ein = ein        
        self.pledge_ngo = None
        self.irsxml_ngo = None
        self.irszip_ngo = None
        self.guidestar_ngo = None
        self.charitynavigator_ngo = None
        self.fcr_ngo = None
        self.guidestarindia_ngo = None

        # Use select_related and prefetch_related to minimize database queries
        self.all_xml_eins = IrsXML_NGO.objects.filter(govt_reg_number=ein).select_related('govt_reg_number')
        with suppress(IrsXML_NGO.DoesNotExist):
            self.irsxml_ngo = self.all_xml_eins.get(govt_reg_number=ein)
        
        with suppress(PledgeNGO.DoesNotExist):
            self.pledge_ngo = PledgeNGO.objects.get(govt_reg_number=ein)
        
        with suppress(IrsZIP_NGO.DoesNotExist):
            self.irszip_ngo = IrsZIP_NGO.objects.get(govt_reg_number=ein)
        
        with suppress(GuidestarNGO.DoesNotExist):
            self.guidestar_ngo = GuidestarNGO.objects.get(govt_reg_number=ein)
        
        with suppress(CharityNavigatorNGO.DoesNotExist):
            self.charitynavigator_ngo = CharityNavigatorNGO.objects.get(govt_reg_number=ein)
        
        with suppress(FCR_NGO.DoesNotExist):
            self.fcr_ngo = FCR_NGO.objects.get(govt_reg_number=ein)
        
        with suppress(GuideStarIndiaNGO.DoesNotExist):
            self.guidestarindia_ngo = GuideStarIndiaNGO.objects.get(govt_reg_number=ein)

        self.merged_data = {}
        self.domain_list = [] 
        self.urls_scraped_list = []
    
    def merge_data(self):
        return {
            "organization_name": self.get_organization_name(),
            "organization_address": self.get_organization_address(),
            "country": self.get_country(),
            "state": self.get_state(),
            "cause": self.get_cause(),
            "email": self.get_email(),
            "phone": self.get_phone(),
            "website": self.get_website(),
            "mission": self.get_mission(),
            "description": self.get_description(),
            "registration_date_year": self.get_registration_date_year(),
            "registration_date_month": self.get_registration_date_month(),
            "registration_date_day": self.get_registration_date_day(),
            "gross_income": self.get_gross_income(),
            "image": self.get_image(),
            "domain" : self.merge_list(self.domain_list),
            "urls_scraped" : self.merge_list(self.urls_scraped_list),
            "has_merged": True,
        } 
    
    def merge_list(self, domain_list:list):
        valid_domain_list = []
        if len(domain_list) == 0:
            return None
        for domain in domain_list:
            rev_list = reverse_list(domain)
            for rev in rev_list:
                valid_domain_list.append(rev)
        unique_domain_list = list(set(valid_domain_list))
        return format_list(unique_domain_list)


    def get_organization_name(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.organization_name:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.organization_name
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.organization_name:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.organization_name
        if self.pledge_ngo:
            if self.pledge_ngo.organization_name:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.organization_name
        if self.irsxml_ngo: 
            in_irs_xml = special_case_org_name(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.organization_name:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.organization_name
        if self.irszip_ngo:
            if self.irszip_ngo.organization_name:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.organization_name
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.organization_name:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.organization_name
        if self.fcr_ngo:
            if self.fcr_ngo.organization_name:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.organization_name
        return None

    def get_organization_address(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.organization_address:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.organization_address
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.organization_address:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.organization_address
        if self.pledge_ngo:
            if self.pledge_ngo.organization_address:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.organization_address
        in_irs_xml = special_case_org_address(self.ein, self.all_xml_eins)
        if in_irs_xml:
            if in_irs_xml.organization_address:
                self.domain_list.append(in_irs_xml.domain)
                self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                return in_irs_xml.organization_address
        
        if self.irszip_ngo:
            if self.irszip_ngo.organization_address:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.organization_address
                
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.organization_address:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.organization_address
        
        if self.fcr_ngo:
            if self.fcr_ngo.organization_address:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.organization_address
        return None
    def get_country(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.country:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.country
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.country:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.country
        if self.pledge_ngo:
            if self.pledge_ngo.country:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.country
        if self.irsxml_ngo:
            in_irs_xml = special_case_country(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.country:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.country
        if self.irszip_ngo:
            if self.irszip_ngo.country:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.country
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.country:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.country
        if self.fcr_ngo:
            if self.fcr_ngo.country:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.country
        return None

    def get_state(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.state:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.state
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.state:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.state
        if self.pledge_ngo:
            if self.pledge_ngo.state:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.state
        if self.irsxml_ngo:
            in_irs_xml = special_case_state(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.state:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.state
        if self.irszip_ngo:
            if self.irszip_ngo.state:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.state
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.state:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.state
        if self.fcr_ngo:
            if self.fcr_ngo.state:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.state
        return None

    def get_cause(self):
        if self.pledge_ngo:
            if self.pledge_ngo.cause:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.cause
        if self.guidestar_ngo:
            if self.guidestar_ngo.cause:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.cause
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.cause:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.cause
        if self.irsxml_ngo:
            in_irs_xml = special_case_cause(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.cause:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.cause
        if self.irszip_ngo:
            if self.irszip_ngo.cause:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.cause
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.cause:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.cause
        if self.fcr_ngo:
            if self.fcr_ngo.cause:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.cause
        return None
    
    def get_email(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.email:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.email
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.email:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.email
        if self.pledge_ngo:
            if self.pledge_ngo.email:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.email
        if self.irsxml_ngo: 
            in_irs_xml = special_case_email(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.email:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.email
        if self.irszip_ngo:
            if self.irszip_ngo.email:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.email
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.email:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.email
        if self.fcr_ngo:
            if self.fcr_ngo.email:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.email
        return None

    def get_phone(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.phone:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.phone
        if self.pledge_ngo:
            if self.pledge_ngo.phone:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.phone
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.phone:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.phone
        if self.irsxml_ngo:
            in_irs_xml = special_case_phone(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.phone:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.phone
        if self.irszip_ngo:
            if self.irszip_ngo.phone:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.phone
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.phone:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.phone
        if self.fcr_ngo:
            if self.fcr_ngo.phone:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.phone
        return None
   
    def get_website(self):
        if self.pledge_ngo:
            if self.pledge_ngo.website:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.website
        if self.guidestar_ngo:
            if self.guidestar_ngo.website:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.website
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.website:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.website
        if self.irsxml_ngo:
            in_irs_xml = special_case_website(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.website:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.website
        if self.irszip_ngo:
            if self.irszip_ngo.website:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.website
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.website:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.website
        if self.fcr_ngo:
            if self.fcr_ngo.website:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.website
        return None

    def get_mission(self):
        if self.pledge_ngo:
            if self.pledge_ngo.mission:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)    
                return self.pledge_ngo.mission
        if self.guidestar_ngo:
            if self.guidestar_ngo.mission:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.mission
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.mission:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.mission
        if self.irsxml_ngo:
            in_irs_xml = special_case_mission(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.mission:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.mission
        if self.irszip_ngo:
            if self.irszip_ngo.mission:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.mission
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.mission:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.mission
        if self.fcr_ngo:
            if self.fcr_ngo.mission:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.mission
        return None
    def get_description(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.description:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.description
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.description:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.description
        if self.pledge_ngo:
            if self.pledge_ngo.description:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.description
        if self.irsxml_ngo:
            in_irs_xml = special_case_description(self.ein, self.all_xml_eins)
            if in_irs_xml:
                if in_irs_xml.description:
                    self.domain_list.append(in_irs_xml.domain)
                    self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                    return in_irs_xml.description
        if self.irszip_ngo:
            if self.irszip_ngo.description:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.description
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.description:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.description
        if self.fcr_ngo:
            if self.fcr_ngo.description:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.description
        return None

    def get_registration_date_year(self):
        if self.guidestar_ngo:
            if self.guidestar_ngo.registration_date_year:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.registration_date_year
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.registration_date_year:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.registration_date_year
        if self.pledge_ngo:
            if self.pledge_ngo.registration_date_year:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.registration_date_year
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.registration_date_year:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.registration_date_year
        in_irs_xml = special_case_registration_date_year(self.ein, self.all_xml_eins)
        if in_irs_xml:
            if in_irs_xml.registration_date_year:
                self.domain_list.append(in_irs_xml.domain)
                self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                return in_irs_xml.registration_date_year
        if self.irszip_ngo:
            if self.irszip_ngo.registration_date_year:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.registration_date_year
        if self.fcr_ngo:
            if self.fcr_ngo.registration_date_year:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.registration_date_year
        return None

    def get_registration_date_month(self):
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.registration_date_month:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.registration_date_month
        return None
    
    def get_registration_date_day(self):
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.registration_date_day:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
            return self.guidestarindia_ngo.registration_date_day
        return None
    
    def get_gross_income(self):
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.gross_income:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.gross_income
        in_irs_xml = special_case_gross_income(self.ein, self.all_xml_eins)
        if in_irs_xml:
            if in_irs_xml.gross_income:
                self.domain_list.append(in_irs_xml.domain)
                self.urls_scraped_list.append(in_irs_xml.urls_scraped)
                return in_irs_xml.gross_income
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.gross_income:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.gross_income
        if self.guidestar_ngo:
            if self.guidestar_ngo.gross_income:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.gross_income
        
        if self.irszip_ngo:
            if self.irszip_ngo.gross_income:
                self.domain_list.append(self.irszip_ngo.domain)
                self.urls_scraped_list.append(self.irszip_ngo.urls_scraped)
                return self.irszip_ngo.gross_income
        if self.fcr_ngo:
            if self.fcr_ngo.gross_income:
                self.domain_list.append(self.fcr_ngo.domain)
                self.urls_scraped_list.append(self.fcr_ngo.urls_scraped)
                return self.fcr_ngo.gross_income
        if self.pledge_ngo:
            if self.pledge_ngo.gross_income:
                return self.pledge_ngo.gross_income
        return None

    def get_image(self):
        if self.pledge_ngo:
            if self.pledge_ngo.image:
                self.domain_list.append(self.pledge_ngo.domain)
                self.urls_scraped_list.append(self.pledge_ngo.urls_scraped)
                return self.pledge_ngo.image
        if self.guidestar_ngo:
            if self.guidestar_ngo.image:
                self.domain_list.append(self.guidestar_ngo.domain)
                self.urls_scraped_list.append(self.guidestar_ngo.urls_scraped)
                return self.guidestar_ngo.image
        if self.guidestarindia_ngo:
            if self.guidestarindia_ngo.image:
                self.domain_list.append(self.guidestarindia_ngo.domain)
                self.urls_scraped_list.append(self.guidestarindia_ngo.urls_scraped)
                return self.guidestarindia_ngo.image
        if self.charitynavigator_ngo:
            if self.charitynavigator_ngo.image:
                self.domain_list.append(self.charitynavigator_ngo.domain)
                self.urls_scraped_list.append(self.charitynavigator_ngo.urls_scraped)
                return self.charitynavigator_ngo.image
        return None



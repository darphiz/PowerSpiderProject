from contextlib import suppress
import re
import logging
from c_navigator.models import NGO
from c_navigator.utils import get_full_region_name, q_builder
from ngo_scraper.notification import Notify
from ngo_scraper.requests import CleanData, CauseGenerator, ProxyRequestClient
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger(__name__)
HOOK = settings.CHARITY_HOOK

def is_int_or_float(s):
    """
    Returns True if the string is an int or a float.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False
    except Exception:
        return False
    
    

class CharityNavigatorScraper(
    ProxyRequestClient, 
    CauseGenerator, 
    CleanData,
    Notify):
   
    def __init__(self, page:int = 1, max_result:int=10) -> None:
        self.page = page
        self.max_result = max_result
        self.base_url = "https://graph.charitynavigator.org/graphql" 
        self.c_url = "https://www.charitynavigator.org/ein/" 
        self.scraped_data = []
        self.webhook_url = HOOK
        super().__init__()
        
    def _get_org_mission(self, soup):
        with suppress(Exception):
            mission_selector = "body > div.mobile-top-padding > div.wrapper.content-well > div > div > div.col-md.col-sm.col-12.order-2.order-sm-2.order-md-1 > div.section.profile-main-content.row > div > div:nth-child(5) > div > p:nth-child(3)"
            if mission := soup.select_one(mission_selector):
                return self.clean_text(mission.text)
        return None
    
    def _generate_org_address(self,soup):
        with suppress(Exception):
            addr_selector = "body > div.mobile-top-padding > div.wrapper.content-well > div > div > div.col-md.col-sm.col-12.order-2.order-sm-2.order-md-1 > div.section.profile-main-content.row > div > div.charity-profile-bullets.row-no-margin-mobile.row > div:nth-child(2) > p:nth-child(2)"
            if addr := soup.select_one(addr_selector):
                spans_list = addr.find_all("span")
                address_by_span = [span.text for span in spans_list]
                new_addr = ", ".join(address_by_span)
                return self.clean_text(new_addr)
        return None
      
    def _generate_org_address_2(self,data):
        street = data.get("street")
        street2 = data.get("street2")
        city = data.get("city")
        state = data.get("state")
        zip_code = data.get("zip")
        addr = [street, street2, city, state, zip_code]
        non_empty_addr = [a for a in addr if a]
        return ", ".join(non_empty_addr)   
        
    def get_year(self, string):
        return match.group() if (match := re.search(r'\d{4}', string)) else None

    
    def _get_registration_year(self, soup):  
        with suppress(Exception):
            reg_wrapper_selector = "body > div.mobile-top-padding > div.wrapper.content-well > div > div > div.col-md.col-sm.col-12.order-2.order-sm-2.order-md-1 > div.section.profile-main-content.row > div > div:nth-child(5) > div > p:nth-child(1)"
            if reg_wrapper := soup.select_one(reg_wrapper_selector):
                reg_year = self.get_year(reg_wrapper.text)
                reg_year = self.clean_number(reg_year)
                return reg_year
        return None
    
    def _get_gross_income(self, soup):
        with suppress(Exception):
            if script := soup.find(
                'script', text=lambda t: 'function drawRevExpChart1' in t if t else False
            ):
                return (
                    script.text.split('data.addRows([')[-1]
                    .split(']);')[0]
                    .strip()
                    .split(',')[-2]
                )
            else:
                return None    
        return None
     
     
    def _gross_income(self, soup):
        gross_income = self._get_gross_income(soup)
        if gross_income:
            if is_int_or_float(gross_income):
                return gross_income
        return None
            
    def _get_org_website_from_soup(self, soup):
        with suppress(Exception):
            selector = "body > div.mobile-top-padding > div.wrapper.content-well > div > div > div.col-md.col-sm.col-12.order-2.order-sm-2.order-md-1 > div.section.profile-main-content.row > div > div.charity-profile-bullets.row-no-margin-mobile.row > div:nth-child(2) > p:nth-child(1) > span > a"
            if website := soup.select_one(selector):
                return self.clean_link(website.text)
        return None
    
    def _parse_mission(self, string):
        if not string:
            return ""
        start = "(more)"
        end = "(less)"
        if start in string and end in string:
            return re.search(r'\(more\)(.*?)\(less\)', string)[1]
        return string    
    
    
    def get_other_data(self, endpoint, data):
        res = self.query(endpoint)
        if res.status_code != 200:
            return None, None, None, None, None
        soup = BeautifulSoup(res.text, "html.parser")
        organization_mission = self._parse_mission(self._get_org_mission(soup)).strip()  
        registration_year = self._get_registration_year(soup)
        gross_income = self.clean_number(self._gross_income(soup))
        org_addr = self._generate_org_address(soup) or self._generate_org_address_2(data)
        website = data.get("website").lower() if data.get("website") else self._get_org_website_from_soup(soup)
        return organization_mission, registration_year, gross_income, org_addr, website    
    
    def _org_already_exist(self, ein):
        if not ein:
            return False
        return NGO.objects.filter(govt_reg_number = ein).exists()
        
                
    def extract_data(self, data):    
        url_scraped = f"{self.c_url}{data.get('ein')}"
        ein = data.get("ein", None)
        # check if the ein is already in the database
        if self._org_already_exist(ein):
            return
        
        other_data = self.get_other_data(url_scraped, data)
        organization_mission = other_data[0]        
        registration_year = other_data[1]
        gross_income = other_data[2]
        org_addr = other_data[3]
        org_website = other_data[4]
        ngo_data = {
            "organization_name": data.get("name"),
            "organization_address": org_addr,
            "country": "United States of America",
        }
        ngo_data["state"] = get_full_region_name(data.get("state"))
        ngo_data["cause"] = self.generator_get_causes([data.get("cause"), ])
        ngo_data["website"] = org_website
        ngo_data["mission"] = organization_mission
        ngo_data["govt_reg_number"] = data.get("ein")
        ngo_data["govt_reg_number_type"] = "EIN"
        ngo_data["registration_date_year"] = registration_year
        ngo_data["gross_income"]  = gross_income
        ngo_data["domain"] = self.format_list(["https://www.charitynavigator.org", ])
        ngo_data["urls_scraped"] = self.format_list([url_scraped, ])
        self.scraped_data.append(ngo_data)
        return

    def crawl(self, payload: dict = None):
        # payload = payload if payload else q_builder(page = self.page, result_size=self.max_result)
        response = self.post_json(self.base_url, json=payload)
        if response.status_code != 200:
            return self._log_error(reason=response.text)
        response = response.json()
        try:
            data = response.get("data").get("publicSearchFaceted").get("results")
        except Exception as e:
            return self._log_error(reason=str(e))
        for d in data:
            self.extract_data(d)
        return self.scraped_data


    def get_max_result(self, payload:dict):
        try:
            response = self.post_json(self.base_url, json=payload)
            if response.status_code != 200:
                return self._log_error(reason=response.text)
            response = response.json()    
            return response.get("data").get("publicSearchFaceted").get("result_count")
        except Exception:
            logger.error(f"Error getting max result")
            print("Error getting max result")
            return 1000

    def _log_error(self,reason=None):
        logger.error(f"Error in crawling page {self.page} \nTraceback: \n{reason}")
        self.alert(
            Notify.error(
                f"Error in crawling page {self.page}"
            )
        )
        return None
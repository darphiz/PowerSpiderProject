import logging
from contextlib import suppress
from datetime import timedelta
from guidestar_app.models import SessionTracker
from guidestar_app.utils import get_full_region_name
from ngo_scraper.notification import Notify
from ngo_scraper.requests import CleanData, CauseGenerator, Helper, ImageDownloader, ProxyRequestClient
from bs4 import BeautifulSoup
import json
from django.utils import timezone
import re
from django.conf import settings

log = logging.getLogger(__name__)
HOOK = settings.GUIDESTAR_HOOK
class GuideStarException(Exception):
    pass

class GuideStarIndexer(ProxyRequestClient):
    def __init__(self, start_page, end_page) -> None:
        self.base_url = "https://www.guidestar.org/nonprofit-directory/arts-culture-humanities/service-other/"
        self.start_page = start_page
        self.end_page = end_page
        self.all_data = []
        if start_page > end_page:
            raise GuideStarException("start_page cannot be greater than end_page") 
        return super().__init__()

    def get_page_numbers(self):
        return range(self.start_page, self.end_page + 1)

    def create_url(self, page_number):
        return f"{self.base_url}{page_number}.aspx"
    def create_urls(self):
        return [self.create_url(page_number) for page_number in self.get_page_numbers()]
    
    def crawl(self):
        all_urls = self.create_urls()
        for url in all_urls:
            data = []
            try:
                data = self.scrape(url)
            except Exception as e:
                log.error(e)            
            if data:
                self.all_data.extend(data)
        return self.all_data
    
    def extract_divs(self, soup):
        parent_div_selector = "#ctl00_divPageContainer > div.page-content > div.float-collection > div.column-75l"
        if parent_div := soup.select_one(parent_div_selector):
            return parent_div.find_all("div", recursive=False)[:3]
        else:
            raise GuideStarException("Parent div not found")
    def get_link_data(self, div):
        all_links = div.find_all("a")
        return [link.attrs["href"] for link in all_links if "href" in link.attrs]
                
    def scrape(self, url):
        response = self.query(url)
        if response.status_code != 200:
            raise GuideStarException(f"Error scraping {url} - {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        if divs := self.extract_divs(soup):
            compiled_list =  [self.get_link_data(div) for div in divs]
            return [item for sublist in compiled_list for item in sublist]
        else:
            raise GuideStarException("No divs found")
        
class GuideStarScraper(
            ProxyRequestClient, 
            CleanData, 
            CauseGenerator, 
            ImageDownloader,
            Helper,
            Notify
            ):
    """
    This will scrape all indexed url
    """
    def __init__(self, url:str="", initial_data:dict = {}) -> None:
        self.url = url
        self.base_url = "https://www.guidestar.org"
        self.endpoint = f"{self.base_url}{self.url}"
        self.organization_address = ""
        self.organization_name = ""
        self.image_path = "images/guidestar/"
        self.webhook_url = HOOK
        self.initial_data = initial_data
        return super().__init__()
    
    def login(self):
        username = settings.GUIDESTAR_USERNAME
        password = settings.GUIDESTAR_PASSWORD
        url = "https://www.guidestar.org/Account/LoginToMainsite?Length=7"
        
        with suppress(Exception):
            if latest_db_session := SessionTracker.objects.all().order_by("-created")[0]:
                # ensure the session is not older than 30 minutes
                if latest_db_session.created < timezone.now() - timedelta(minutes=30):
                    print("Deleting old session")
                    latest_db_session.delete()
                    return self.login()
                
                db_cookie_string = latest_db_session.cookies
                db_cookie_dict = json.loads(db_cookie_string)
                self.client()
                self.session.cookies.update(db_cookie_dict)
                return
        
        response = self.post_data(url, data={
            "EmailAddress": username, 
            "Password": password,
            "IsUpdaterUserTransfer" : False,
            "UpdaterInviteId": "",
            'X-Requested-With' : 'XMLHttpRequest'
            })
        if response.status_code != 200:
            log.error(f"Error logging in to guide star - {response.status_code}")
            self.alert(
                Notify.error(
                    f"Error logging in to guide star - {response.status_code}"
                )
            )
            raise GuideStarException("Cannot login")
        cookies = response.cookies
        self.session.cookies.update(cookies)
        cookies_dict = response.cookies.get_dict()
        cookie_string = json.dumps(cookies_dict)
        SessionTracker.objects.create(cookies=cookie_string)
        return
        
    def is_email(self, email_addr):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email_addr)
    
    def _get_org_one(self, soup):
        with suppress(Exception):
            selector = "#profileHeader > div.col-lg-9 > h1"
            if organization_name := soup.select_one(selector):
                org_name = self.clean_text(organization_name.text) 
                if not org_name:
                    raise GuideStarException("No organization name")
                self.organization_name = org_name
                return org_name
        return None
    
    def _get_org_two(self, soup):
        with suppress(Exception):
            org_name_h = soup.find("h1", class_="profile-org-name")
            if org_name_h:
                org_name = self.clean_text(org_name_h.text)
                if not org_name:
                    raise GuideStarException("No organization name")
                self.organization_name = org_name
                return org_name
        return None
    
    def _get_organization_name(self, soup):
        org_name = self._get_org_one(soup) or self._get_org_two(soup)
        if not org_name:
            raise GuideStarException("No organization name")
        self.organization_name = org_name
        return org_name
        
    
    def _get_organization_address(self, soup):
        merged_address = ""
        with suppress(Exception):
            targeted_p = soup.find_all("p", class_ ="report-section-header")
            for p in targeted_p:
                if self.clean_text(p.text) == "main address":
                    get_parent = p.parent
                    # the organization address is in all the p tags except the first one and stops at the next div tag or p tag with class "addresses"
                    for p in get_parent.find_all("p")[1:]:
                        if p.attrs.get("class") == ["addresses"] or p.name == "div":
                            break
                        merged_address += f" {p.text}"
                    merged_address = merged_address.strip()
                    self.organization_address = merged_address
        return self.clean_text(merged_address)
    
    
    def _get_country(self):
        with suppress(Exception):
            address = self.organization_address
            words = address.split()
            country = next(
                (
                    " ".join(words[i + 1 :])
                    for i, word in enumerate(words)
                    if word.isdigit() and len(word) >= 5
                ).strip(),
                "United States of America",
            ) 
            
            return self.clean_country(country) 
        return "United States of America"
    
    def _get_state(self):
        with suppress(Exception):
            address = self.organization_address
            words = address.split()
            state_code = next(
                (
                    word
                    for word in words
                    if len(word) == 2 and word.isalpha() and word.isupper() and word != "US" and word.upper() != "PO"
                ),
                "",
            )
            country = self.clean_text(self._get_country())
            if country in ["united states", "usa", "us", "u.s.a", "u.s", "u.s.a.", "u.s.","united state", 
                            "united states of america.", "united states of america"]:
                return get_full_region_name(state_code)
            return state_code
        return ""
    
    def _get_cause(self, soup):
        with suppress(Exception):
            major_selector = "#summary > div:nth-child(3)"
            if major := soup.select_one(major_selector):    
                return self._extract_cause(major)
        return None

    def _extract_cause(self, major):
        second_section = major.find_all("section")[1]
        causes_tags = second_section.find_all("p")[1:]
        causes = [self.clean_text(cause.text) for cause in causes_tags]
        remove_empty = [cause for cause in causes if cause]
        return self.generator_get_causes(remove_empty)
        
    def _get_email(self, soup):
        with suppress(Exception):
            class_name = "__cf_email__"
            if email := soup.find_all("a", class_=class_name):
                encoded_email = email[0].get("data-cfemail")
                email_addr = self.clean_emails(self.decode_email(encoded_email))
                return email_addr if self.is_email(email_addr) else None
        return None
        
    def _get_phone(self, soup):
        with suppress(Exception):
            class_ = "report-section-text"
            if phone := soup.find_all("p", class_=class_):
                for p in phone:
                    if p.text.strip().startswith("Fundraising contact phone"):
                        return self.clean_phone(p.text.split(":")[1].strip())
        return None
        
    def _get_website(self, soup):
        with suppress(Exception):
            if website := soup.find("span", class_="website"):
                link = website.find("a")
                return self.clean_link(link.get("href"))
        return None
    
    def _get_mission(self, soup):
        ignore_sentence = "this organization has not provided guidestar with a mission statement."
        with suppress(Exception):
            if mission_p := soup.find("p", id="mission-statement"):
                mission_statement = mission_p.text.strip()
                if mission_statement.lower() != ignore_sentence.lower():
                    return self.clean_text(mission_statement)                
        return None
    
    def _get_government_number(self, soup):
        with suppress(Exception):
            section_header =  soup.find_all("p", class_="report-section-header")
            for p in section_header:
                if p.text.strip() == "EIN":
                    next_sibling = p.find_next_sibling("p")
                    return self.clean_number(next_sibling.text.strip())
        return None

    def _get_reg_date_year(self, soup):
        title_tags = soup.find_all("p", class_="report-section-header")
        for p in title_tags:
            if p.text.strip().startswith("Ruling"):
                next_sibling = p.find_next_sibling("p")
                return next_sibling.text.strip()
        return None    
    
    def _get_image(self, soup):
        try:
            if img := soup.find("img", class_="logo"):
                src = img.get("src")
                link = f"{self.base_url}{src}"
                link = [link, ]
                return self.download_images(
                    link, self.image_path, base_name=self.organization_name.strip()
                )
        except Exception:
            log.error(f"Error getting image for {self.organization_name} , {self.endpoint}")
        return None
    
    
    def scrape(self):
        # self.login()
        response = self.query(self.endpoint)
        if response.status_code != 200:
            log.error(f"Error scraping {self.endpoint} - {response.status_code}")
            raise Exception(f"Error scraping {self.endpoint} - {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        if self.initial_data.get("organization_name", None):
            self.organization_name = self.initial_data.get("organization_name", None)
        
        data = {
            "organization_name": self.initial_data.get("organization_name", None) or self._get_organization_name(soup),
        }
        
        data ["organization_address"] = self._get_organization_address(soup)
        data["country"] = self.clean_text(self._get_country())
        data["state"] = self.initial_data.get("state", None) or self.clean_text(self._get_state())
        data["cause"] = self.clean_text(self._get_cause(soup))
        data["email"] = self._get_email(soup)
        data["phone"] = self.clean_phone(self._get_phone(soup))
        data["website"] = self.clean_link(self._get_website(soup))
        data["mission"] = self.clean_text(self._get_mission(soup))
        data["govt_reg_number"] = self.initial_data.get("govt_reg_number", None) or self.clean_number(self._get_government_number(soup)).replace("-", "")
        data["govt_reg_number_type"] = "EIN" if data.get("govt_reg_number") else None
        data["registration_date_year"] = self.clean_number(self._get_reg_date_year(soup))
        data["image"] = self._get_image(soup)
        data["domain"] = self.format_list([self.base_url,])
        data["urls_scraped"] = self.format_list([self.endpoint,])
        return data
    
    def scrape_image_only(self, url):
        self.endpoint = url
        response = self.query(url)
        if response.status_code != 200:
            log.error(f"Error scraping {self.endpoint} - {response.status_code}")
            raise Exception(f"Error scraping {self.endpoint} - {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        data = {
            "organization_name": self._get_organization_name(soup),
        }
        data["govt_reg_number"] = self.initial_data.get("govt_reg_number", None) or self.clean_number(self._get_government_number(soup)).replace("-", "")
        data["govt_reg_number_type"] = "EIN" if data.get("govt_reg_number") else None
        data["image"] = self._get_image(soup)
        return data
    
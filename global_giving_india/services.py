import re
import logging
import contextlib
from bs4 import BeautifulSoup
from global_giving_india.parser import RetrieveLinks
from ngo_scraper.requests import CleanData, CauseGenerator, ImageDownloader, ProxyRequestClient
from ngo_scraper.notification import Notify
from django.conf import settings
from .models import GuideStarIndiaIndexedUrl



logger = logging.getLogger(__name__)

HOOK = settings.GGI_HOOK

class GG_India_Indexer(RetrieveLinks):
    def __init__(self, file):
        self.file = file
        return super().__init__(file)        
        
    def extract(self):
        return self.crawl_file()
    
    def index_all(self):
        urls = self.extract()
        for url in urls:
            with contextlib.suppress(Exception):
                GuideStarIndiaIndexedUrl.objects.create(url=url)
        return urls
    
    
class GG_India_Scraper(
            ProxyRequestClient, 
            CleanData, 
            CauseGenerator, 
            ImageDownloader,
            Notify
):
    def __init__(self, url):
        self.url = url
        self.ggi_data = {
            "country": "India",
        }
        self.domain = "https://guidestarindia.org.in/"
        self.image_path = "images/gg_india/"
        self.organization_name = None
        self.profile_url = self.url.replace("Summary", "Organisation")
        self.finance_url = self.url.replace("Summary", "Finances")
        self.webhook_url = HOOK
        return super().__init__()
    
    def _get_organization_name(self, soup):
        with contextlib.suppress(Exception):
            selector = "#SectionPlaceHolder1_ctl01_ctpTxtCharityName > div > span:nth-child(2)"
            if span := soup.select_one(selector):
                org_name = self.clean_text(span.text.strip())
                self.organization_name = org_name
                return org_name
        return None
    
    def _get_org_address(self, soup):  # sourcery skip: extract-method
        with contextlib.suppress(Exception):
            sid = "#SectionPlaceHolder1_ctl01_TextPlaceHolder15"
            if first_span := soup.select_one(sid):
                all_spans_sibling = first_span.find_next_siblings("span")
                all_spans = all_spans_sibling
                all_spans = all_spans[:-1]
                all_span_text = [span.text.strip() for span in all_spans]
                # loop through all_span_text and remove and stop at the zip code
                for i, text in enumerate(all_span_text):
                    if text.isdigit() and len(text) == 6:
                        all_span_text = all_span_text[:i+1]
                        break
                return self.clean_text(" ".join(all_span_text))
        return None
    
    def _get_state(self, soup):
        with contextlib.suppress(Exception):
            sid = 'Anthem_SectionPlaceHolder1_ctl01_ccAddrState_ctl01__'
            if state := soup.find(id=sid):
                return self.clean_text(state.text.strip())
        return None

    def _get_all_cause(self, soup):
        with contextlib.suppress(Exception):
            ul_selector = "#Anthem_SectionPlaceHolder1_ctl01_classificationList_ctl01__ > fieldset > ul"
            ul = soup.select_one(ul_selector)
            all_li = ul.find_all("li")
            all_li_text = [li.text.strip().lower() for li in all_li]
            return self.generator_get_causes(all_li_text, 60)
        return None
    
    def _get_email(self, soup):
        with contextlib.suppress(Exception):
            sid = "SectionPlaceHolder1_ctl01_textEmail_desc"
            if span := soup.find(id=sid):
                return (
                    self.clean_emails(mail_to.text.strip())
                    if (
                        mail_to := span.find_next_sibling(
                            "a", href=lambda href: href and href.startswith("mailto")
                        )
                    )
                    else None
                )
            else:
                return None
        return None
    
    def _get_phone(self, soup):
        with contextlib.suppress(Exception):
            div_class = "CTPParaClippingHeaderLabel"
            if divs := soup.find_all("div", class_=div_class):
                for div in divs:
                    if "Telephone" in div.text.strip():
                        phone = div.find_next_sibling("div").text.strip()
                        phone = self.clean_phone(phone) 
                        return phone.replace(" ", "")
        return None
    
    def _get_website(self, soup):
        with contextlib.suppress(Exception):
            sid = "SectionPlaceHolder1_ctl01_textWeb_desc"
            span = soup.find(id=sid)        
            if website := span.find_next_sibling(
                "a", href=lambda href: href and href.startswith("http")
            ):
                return self.clean_link(website.text.strip())
        return None
    
    def _get_mission(self, soup):
        with contextlib.suppress(Exception):
            sid = "SectionPlaceHolder1_ctl01_TextControl37"
            if div := soup.find(id=sid):
                texts = div.get_text().strip()
                return self.clean_text(texts.replace("Vision", "", 1))
        return None

    
    def _get_org_description(self, soup):
        with contextlib.suppress(Exception):
            sid = "SectionPlaceHolder1_ctl01_TextControl7_desc"
            if div := soup.find(id=sid):
                next_span = div.find_next_sibling("span")
                return self.clean_text(next_span.text.strip())       
        return None
       
    def _get_govt_reg_no(self, soup):
        selector = "#SectionPlaceHolder1_ctl01_txtPriReg > div > span.inline_with_space_below"
        with contextlib.suppress(Exception):
            if span := soup.select_one(selector):
                return span.text.strip()
        return None     
    
    def _get_reg_type(self, soup):
        selector = "#SectionPlaceHolder1_ctl01_txtPriReg_lbl"
        with contextlib.suppress(Exception):
            if span := soup.select_one(selector):
                reg_type = span.text.strip()
                reg_type = re.sub(r'\([^)]*\)', '', reg_type) 
                return self.clean_text(reg_type)
        return None

    def _get_reg_year(self, soup):
        sid = "SectionPlaceHolder1_ctl01_TextControl27_desc"
        with contextlib.suppress(Exception):
            if div := soup.find(id=sid):
                next_span = div.find_next_sibling("span")
                return self.clean_number(next_span.text.strip())
        return None
    
    def _get_reg_date(self, soup):
        sid = "SectionPlaceHolder1_ctl01_dynLegalReg_ctl10_DateControl1"
        with contextlib.suppress(Exception):
            if div := soup.find(id=sid):
                all_text = div.get_text().strip()
                # remove "Registration date" from text
                remove_text = all_text.replace("Registration date", "")
                remove_text = remove_text.strip()
                dd, mm, _= remove_text.split("/")
                return dd, mm
            
        return (None, None)
    
    def _get_gross_income(self, soup):
        income_table_id = "SectionPlaceHolder1_ctl01_incomeTable"
        income_decimal = 0.0
        with contextlib.suppress(Exception):
            if table := soup.find(id=income_table_id):
                all_tr = table.find_all("tr")
                income_class = "CTPFinancialSectionTotalAmount"
                for tr in all_tr:
                    if tr.find("td", class_=income_class):
                        income = tr.find("td", class_=income_class).get_text().strip()
                        income = self.clean_number(income)
                        income_decimal = float(income)
        return None if income_decimal == 0.0 else int(income_decimal * 100000)
        
        
    
         
    def _get_images(self, soup):
        image_selector = "#SectionPlaceHolder1_ctl01_duLogo > div > div:nth-child(3) > img"
        try:
            link = soup.select_one(image_selector).get("src")
            link = f"{self.domain}{link}"
            links = [link, ]
            return self.download_images(
                        links, self.image_path, base_name=self.organization_name
                    )
        except Exception as e:
            logger.error(f"GG_India_Scraper: {e}")
            self.alert(Notify.error(f"Image Error \n{e}"))
            return None

     
    def scrape(self):
        response = self.query(self.url)
        profile_response = self.query(self.profile_url)
        finance_response = self.query(self.finance_url)
        if response.status_code != 200 or profile_response.status_code != 200 or finance_response.status_code != 200:
            logger.error(f"GG_India_Scraper: {response.status_code}, {profile_response.status_code}")
            self.alert(Notify.error(f"Crawl Error \nSummary Response: {response.status_code} \nProfile Response: {profile_response.status_code} \nFinance Response: {finance_response.status_code}"))
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
        finance_soup = BeautifulSoup(finance_response.text, 'html.parser')
        self.ggi_data['organization_name'] = self._get_organization_name(soup)
        self.ggi_data['organization_address'] = self._get_org_address(soup)        
        self.ggi_data['state'] = self._get_state(soup)
        self.ggi_data['cause'] = self._get_all_cause(profile_soup)
        self.ggi_data['email'] = self._get_email(soup)
        self.ggi_data['phone'] = self._get_phone(soup)
        self.ggi_data['website'] = self._get_website(soup)
        self.ggi_data['mission'] = self._get_mission(profile_soup)
        self.ggi_data['description'] = self._get_org_description(profile_soup)
        self.ggi_data['govt_reg_number'] = self._get_govt_reg_no(soup)
        self.ggi_data['govt_reg_number_type'] = self._get_reg_type(soup)
        self.ggi_data['registration_date_year'] = self._get_reg_year(soup)
        reg_date = self._get_reg_date(profile_soup)
        self.ggi_data["registration_date_day"] = reg_date[0] 
        self.ggi_data['registration_date_month']= reg_date[1]
        self.ggi_data['gross_income'] = self._get_gross_income(finance_soup)
        self.ggi_data["domain"] = self.format_list([self.domain,])
        self.ggi_data["urls_scraped"] = self.format_list([self.url,])
        self.ggi_data["image"] = self._get_images(soup)
        return self.ggi_data

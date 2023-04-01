import logging
from contextlib import suppress
from django.utils.text import slugify
from irs_app.models import IRSIndexedUrl
from ngo_scraper.requests import CleanData, CauseGenerator, ImageDownloader, ProxyRequestClient
from bs4 import BeautifulSoup



log = logging.getLogger(__name__) 

class IrsUrlIndexer:
    def __init__(self) -> None:
        self.file_name = "irs_app/irs_zip/data-download-epostcard.txt"
    
    def _get_endpoint(self, info_str):
        with suppress(Exception):
            base_url = "https://eintaxid.com/company/"
            info_list = info_str.split("|")
            ein = info_list[0]
            name = info_list[2]
            name = slugify(name.lower())
            return f"{base_url}{ein}-{name}"
        return None
    
    def crawl(self) -> None:
        print("Crawling IRS endpoints...")
        with open(self.file_name, 'r') as f:
            counter = 0
            while (line := f.readline()):
                if endpoint := self._get_endpoint(line):
                    IRSIndexedUrl.objects.update_or_create(url = endpoint)    
                counter += 1
                print(f"Processed {counter} lines")
        return
    
    
class IrsScraper(ProxyRequestClient, 
            CleanData, 
            CauseGenerator, 
            ImageDownloader):
    
    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint
        return super().__init__()

    def _get_organization_name(self, soup):
        with suppress(Exception):
            table_heads = soup.find_all("th")
            for table_head in table_heads:
                if table_head.text.strip().startswith("Organization Name"):
                    td = table_head.find_next_sibling("td")
                    return td.text.strip()
        return None

    def _get_organization_address(self, soup):
        with suppress(Exception):
            tds = soup.find_all("table")[1].find_all("td")
            return ("".join(f"{td.text.strip()} " for td in tds)).replace("%", " ").strip()
        return None
    
    def _get_country(self, soup):
        with suppress(Exception):
            # country is in the second table with th of Country
            second_table = soup.find_all("table")[1]
            ths = second_table.find_all("th")
            for th in ths:
                if th.text.strip().startswith("Country"):
                    td = th.find_next_sibling("td")
                    return self.clean_country(td.text.strip())
        return None
    
    
    def _get_state(self, soup):
        with suppress(Exception):
            # state is in the second table with th of State
            second_table = soup.find_all("table")[1]
            ths = second_table.find_all("th")
            for th in ths:
                if th.text.strip().startswith("State"):
                    td = th.find_next_sibling("td")
                    return td.text.strip()
        return None
        
    def _get_reg_number(self):
        with suppress(Exception):
            return self.endpoint.split("/")[-1].split("-")[0]
        return None
       
    def _get_date(self, soup):
        with suppress(Exception):
            # date is in the second table with th of Date
            third_table = soup.find_all("table")[2]
            ths = third_table.find_all("th")
            for th in ths:
                if th.text.strip().startswith("Tax period begin"):
                    td = th.find_next_sibling("td")
                    return td.text.strip()
        return None
     
    def scrape(self):
        response = self.query(self.endpoint)
        if response.status_code != 200:
            log.error(f"Error: error scraping {self.endpoint} - {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        data = {
            "organization_name": (self.clean_text(self._get_organization_name(soup))).strip(),
        }
        data["organization_address"] = self.clean_text(self._get_organization_address(soup))
        data["country"] = self.clean_text(self._get_country(soup)) or "United States of America"
        data["state"] = self.clean_text(self._get_state(soup))
        data["govt_reg_number"] = self.clean_number(self._get_reg_number())
        data["govt_reg_number_type"] = "EIN"
        data["domain"] = self.format_list(["data-download-epostcard.zip",])
        data["urls_scraped"] = self.format_list(["data-download-epostcard.txt",])
        return data
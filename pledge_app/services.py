import logging
from contextlib import suppress
from ngo_scraper.notification import Notify
from ngo_scraper.requests import CauseGenerator, CleanData, ImageDownloader, ProxyRequestClient
from bs4 import BeautifulSoup
from django.conf import settings


logger = logging.getLogger(__name__)

HOOK = settings.PLEDGE_HOOK


class NoDataError(Exception):
    pass

class PledgeListCrawler(ProxyRequestClient, Notify):
    def __init__(self, start=1, end=5, cause="animals"):
        self.start = start
        self.end = end
        self.cause = cause
        self.url = "https://www.pledge.to/organizations"
        self.links = []
        self.webhook_url = HOOK
        return super().__init__()
        
    def crawl_urls(self):
        urls = []
        for i in range(self.start, self.end+1):
            url = f"{self.url}?page={str(i)}&cause={self.cause}"
            urls.append(url)
        return urls

    def crawl(self, url):
        try:            
            response = self.query(url)
            if response.status_code != 200:
                logger.error(f"Error crawling {url}: BAD RESPONSE")
                self.alert(Notify.error(f"Error crawling {url}: BAD RESPONSE"))
                return 
            
            page_soup = BeautifulSoup(response.text, "html.parser")
            data_collection = page_soup.find_all("div", {"class": "col-sm-6"})
            for data in data_collection:
                detail_link = data.find("a", {"class": "featured-fundraiser-link"})
                link = detail_link["href"]
                if link not in self.links and link is not None:
                    self.links.append(link)
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            self.alert(Notify.error(f"#Error crawling {url}: \n{str(e)}"))
        return
        
    def crawl_all(self):
        self.alert(Notify.info(f"Crawling {self.cause} pledges.to from page {self.start} to page {self.end}"))
        urls = self.crawl_urls()
        for url in urls:
            self.crawl(url)
        return self.links



class PledgeScraper(ProxyRequestClient, 
                    CauseGenerator,
                    ImageDownloader,
                    CleanData,
                    Notify
                    ):
    
    def __init__(self, link):
        self.link = link
        self.url = "https://www.pledge.to"
        self.data = []
        self.image_path = "images/pledge/"    
        return super().__init__()
    
    def _patch_url(self):
        return f"{self.url}{self.link}"
    
    def _get_full_region_name(self, short_name):
        with suppress(Exception):
            states = {
                'AK': 'Alaska',
                'AL': 'Alabama',
                'AR': 'Arkansas',
                'AS': 'American Samoa',
                'AZ': 'Arizona',
                'CA': 'California',
                'CO': 'Colorado',
                'CT': 'Connecticut',
                'DC': 'District of Columbia',
                'DE': 'Delaware',
                'FL': 'Florida',
                'GA': 'Georgia',
                'GU': 'Guam',
                'HI': 'Hawaii',
                'IA': 'Iowa',
                'ID': 'Idaho',
                'IL': 'Illinois',
                'IN': 'Indiana',
                'KS': 'Kansas',
                'KY': 'Kentucky',
                'LA': 'Louisiana',
                'MA': 'Massachusetts',
                'MD': 'Maryland',
                'ME': 'Maine',
                'MI': 'Michigan',
                'MN': 'Minnesota',
                'MO': 'Missouri',
                'MP': 'Northern Mariana Islands',
                'MS': 'Mississippi',
                'MT': 'Montana',
                'NA': 'National',
                'NC': 'North Carolina',
                'ND': 'North Dakota',
                'NE': 'Nebraska',
                'NH': 'New Hampshire',
                'NJ': 'New Jersey',
                'NM': 'New Mexico',
                'NV': 'Nevada',
                'NY': 'New York',
                'OH': 'Ohio',
                'OK': 'Oklahoma',
                'OR': 'Oregon',
                'PA': 'Pennsylvania',
                'PR': 'Puerto Rico',
                'RI': 'Rhode Island',
                'SC': 'South Carolina',
                'SD': 'South Dakota',
                'TN': 'Tennessee',
                'TX': 'Texas',
                'UT': 'Utah',
                'VA': 'Virginia',
                'VI': 'Virgin Islands',
                'VT': 'Vermont',
                'WA': 'Washington',
                'WI': 'Wisconsin',
                'WV': 'West Virginia',
                'WY': 'Wyoming'
            }
            state_name = states.get(short_name.upper())
            return short_name.upper() if state_name is None else state_name
        return short_name
    
    def _get_org_address(self, page_soup:BeautifulSoup):
        with suppress(Exception):
            try:
                street_address = page_soup.find("span", {"class": "street-address"}).text
            except Exception as e:
                street_address = ""
            try:
                locality = page_soup.find("span", {"class": "locality"}).text
            except Exception as e:
                locality = ""
            try:
                region = page_soup.find("abbr", {"class": "region"}).text
            except Exception as e:
                region = ""
            try:
                postal_code = page_soup.find("span", {"class": "postal-code"}).text
            except Exception as e:
                postal_code = ""
            try:
                country = page_soup.find("span", {"class": "p-country"}).text
            except Exception as e:
                country = ""
            full_address =  f"{street_address}, {locality}, {region} {postal_code}, {country}"        
            return self.clean_text(full_address), self.clean_text(region), self.clean_text(country)
        return None, None, None
        
    def _get_website_link(self, page_soup:BeautifulSoup):
        with suppress(Exception):
            social_links_ul = page_soup.find("ul", {"class": "social-icons"})
            social_links = social_links_ul.find_all("li")
            website_li = social_links[0]
            return self.clean_link(website_li.find("a").get("href"))
        return None
    
    def _scrape_image(self, page_soup):
        try:
            all_image_url = []
            banner_cover_div = page_soup.find("div", {"class": "bg-cover"})
            if banner_cover_div is None:
                return None
            with suppress(Exception):
                image_url = banner_cover_div["style"].split("url('")[-1].split("')")[0]
                all_image_url.append(image_url) if image_url is not None else None
            
            with suppress(Exception):
                header_div = page_soup.find("header", {"class": "organization-header"})
                _side_image = header_div.find("img")["src"]
                all_image_url.append(_side_image) if _side_image is not None else None
            return all_image_url
        except Exception as e:
            logger.error(f"Error scraping image: {str(e)}")
            return None
        
    def _get_org_mission(self, page_soup:BeautifulSoup):
        with suppress(Exception):
            mission_div = page_soup.find("div", {"class": "organization-mission"})
            mission_section = mission_div.find("section")
            mission_text = mission_section.find_all("p")
            return self.clean_text(" ".join([p.text for p in mission_text]))        
        return None
    
    def _get_causes(self, page_soup:BeautifulSoup):
        with suppress(Exception):
            mission_div = page_soup.find("div", {"class": "organization-mission"})
            cause_section = mission_div.find_all("section")[1]
            cause_ul = cause_section.find("ul")
            causes_li = cause_ul.find_all("li")
            return [li.find("a").text for li in causes_li[1:]]
        return None
        
    def scrape(self):
        response = self.query(self._patch_url())
        if response.status_code != 200:
            logger.error(f"Error scraping {self.link}: {response.status_code}")
            self.alert(Notify.error(f"Error scraping {self.link}: {response.status_code}"))
            return
        page_soup = BeautifulSoup(response.text, "html.parser")
        organization_name = str(page_soup.find("h1", {"class": "h3"}).text)
        full_address, region, country = self._get_org_address(page_soup)
        data = {
            "organization_name": self.clean_text(organization_name),
            "organization_address": full_address,
            "country": self.clean_country(country),
            "state": self._get_full_region_name(region),
        }
        data["cause"] = self.generator_get_causes(self._get_causes(page_soup))
        data["website"] = self._get_website_link(page_soup)
        data["mission"] = self._get_org_mission(page_soup)
        data["image"] = self.download_images(
                self._scrape_image(page_soup),
                self.image_path,
                data["organization_name"]
            )
        data["domain"] = self.format_list([self.url,])
        data["urls_scraped"] = self.format_list([self._patch_url(), ])
        return data






















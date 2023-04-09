import tls_client
import logging
from fake_useragent import UserAgent
import urllib3
from guidestar_app.utils import get_full_region_name
from django.conf import settings
from ngo_scraper.notification import Notify

logger = logging.getLogger(__name__)


urllib3.disable_warnings()


class GGRequest:
    def __init__(self):
        self.session = tls_client.Session(client_identifier="chrome_103")
        self.proxy = settings.PROXY_URL or None
        self.session.headers.update(
            {
                "accept": "application/json, */*;q=0.8",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9",
                'user-agent': UserAgent().random,
                'origin': 'https://www.guidestar.org',
                'referer': 'https://www.guidestar.org/search',
                'x-requested-with': 'XMLHttpRequest',
                "connection": "keep-alive"
            }
        )
        # add proxies
        self.session.proxies.update(
            {
                'http': self.proxy,
                'https': self.proxy,
            }
        )
        
        
    def gg_get(self, url, params=None):
        return self.session.get(url, 
                                params=params, 
                                timeout_seconds=200
                            )
    
    def gg_post(self, url, data=None):
        return self.session.post(url, 
                                 data=data, 
                                 timeout_seconds=200
                            )
    
    
    
class IndexGGUrls(GGRequest, Notify):
    def __init__(self, state, page=1, city=""):
        self.endpoint = 'https://www.guidestar.org/search/SubmitSearch'
        self.state = state
        self.page = page
        self.city = city
        self.webhook_url = settings.GUIDESTAR_HOOK or None
        self.max_results = 400
        return super().__init__()
    
    
    def crawl(self, use_v2:bool=False):
        # generate cookies
        v1_data = {
                'State': self.state, 
                'CurrentPage': self.page,
                'SearchType': 'org',
                }
        
        v2_data = {
                    "CurrentPage": self.page,
                    "SearchType": "org",
                    "State": self.state,
                    "PeopleZipRadius": "Zip Only",
                    "PeopleRevenueRangeLow": "$0",
                    "PeopleRevenueRangeHigh": "max",
                    "PeopleAssetsRangeLow": "$0",
                    "PeopleAssetsRangeHigh": "max",
                    "PCSSubjectPeople": "",
                    "CityNav": self.city,
                    "SelectedCityNav[]": self.city
        }
        
        data = v2_data if use_v2 else v1_data
        response = self.gg_post(self.endpoint, data=data)
        if response.status_code != 200:
            self.alert(f"Error in crawling {self.state} page {self.page} \n Reason: \n{response.status_code}")
            logger.error(f"Error in crawling {self.state} page {self.page}")
            raise Exception(f"Error in crawling {self.state} page {self.page}")
        
        all_urls = response.json() 
        self.max_results = all_urls['TotalHits']
        return all_urls['Hits']

    def scrape(self, use_v2:bool=False):
        try:
            all_ngo = self.crawl(use_v2=use_v2)
            if all_ngo is None:
                return None
            all_ngo_data = []
            for ngo in all_ngo:
                ngo_data = {}
                ngo_data['url'] = f'/profile/{ngo["Ein"]}'
                ngo_data['organization_name'] = ngo['OrgName']
                ngo_data['govt_reg_number'] = ngo.get('Ein', "").replace("-", "")
                ngo_data['govt_reg_number_type'] = "EIN" if ngo_data['govt_reg_number'] else None
                ngo_data["state"] = get_full_region_name(ngo['State'])
                all_ngo_data.append(ngo_data)
            return all_ngo_data
        except Exception as e:
            self.alert(f"Error in crawling {self.state} page {self.page} \n Reason: \n{str(e)}")
            logger.error(f"Error in crawling {self.state} page {self.page} \n Reason: \n{str(e)}")
            raise e


    def get_max_page(self, use_v2:bool=False):
        all_ngo = self.crawl(use_v2=use_v2)
        if all_ngo is None:
            return 400
        return self.max_results // 25 + 1
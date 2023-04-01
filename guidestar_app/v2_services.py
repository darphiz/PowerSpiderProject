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
        self.session = tls_client.Session(
            client_identifier="chrome_103",
            h2_settings={
                "HEADER_TABLE_SIZE": 65536,
                "MAX_CONCURRENT_STREAMS": 5000,
            },
        )
        # self.proxy = settings.PROXY_URL or None
        self.proxy = settings.PROXY_URL or None
        self.session.headers.update(
            {
                'User-Agent': UserAgent().random,
                'origin': 'https://www.guidestar.org',
                'referer': 'https://www.guidestar.org/search',
                'x-requested-with': 'XMLHttpRequest',
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
                                # verify=False, 
                                timeout_seconds=200
                            )
    
    def gg_post(self, url, data=None):
        return self.session.post(url, 
                                 data=data, 
                                #  verify=False, 
                                 timeout_seconds=200
                            )
    
    
    
class IndexGGUrls(GGRequest, Notify):
    def __init__(self, state, page=1):
        self.endpoint = 'https://www.guidestar.org/search/SubmitSearch'
        self.state = state
        self.page = page
        self.webhook_url = settings.GUIDESTAR_HOOK or None
        return super().__init__()
    
    
    def crawl(self):
        # generate cookies
        self.gg_get('https://www.guidestar.org/')
        data = {
                'State': self.state, 
                'CurrentPage': self.page,
                'SearchType': 'org',
                }
        response = self.gg_post(self.endpoint, data=data)
        if response.status_code != 200:
            self.alert(f"Error in crawling {self.state} page {self.page} \n Reason: \n{response.text}")
            logger.error(f"Error in crawling {self.state} page {self.page}")
            return None
        
        all_urls = response.json() 
        return all_urls['Hits']

    def scrape(self):
        try:
            all_ngo = self.crawl()
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
            return None
        
if __name__ == '__main__':
    urls = IndexGGUrls('New Jersey', 400).scrape()
    print(urls)
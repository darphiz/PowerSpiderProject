import re
import uuid
import json
from random import choices
from fake_useragent import UserAgent
import tls_client
import requests
import urllib3
from fuzzywuzzy import fuzz
from cleantext import clean
from retry import retry
from django.utils.text import slugify
from django.conf import settings

class NoDataError(Exception):
    pass


urllib3.disable_warnings()


class Headers:
    def __init__(self) -> None:
        self.user_agent = UserAgent()
        self.referers = [
            "https://www.google.com/", 
            "https://www.bing.com/", 
            "https://www.facebook.com/", 
            "https://www.twitter.com/", 
            ""
        ]
        self.weights = [0.4, 0.1, 0.1, 0.4, 0.05]
    
    def get_random_referer(self):
        return choices(self.referers,weights=self.weights)[0]
    
    def get_random_user_agent(self):
        return self.user_agent.random
    
    def get_headers(self):
        return {
            "Referer": self.get_random_referer(),
            'cache-control': 'max-age=0', 
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 
            'sec-ch-ua-mobile': '?0', 
            'user-agent': self.get_random_user_agent(), 
            'sec-fetch-site': 'none', 
            'sec-fetch-mode': 'navigate', 
            'sec-fetch-user': '?1', 
            'sec-fetch-dest': 'document', 
            'accept-language': 'en-US,en;q=0.9',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }


class ProxyRequestClient(Headers):
    def __init__(self) -> None:
        self.session = None
        self.proxy = settings.PROXY_URL or None
        return super().__init__()
    
    def client(self):
        proxies = {"http": self.proxy, "https": self.proxy}
        session = requests.Session()
        headers =  self.get_headers()
        if self.proxy:
            session.proxies.update(proxies)
        session.headers.update(headers)
        self.session = session
        return session
    
    def query(self, url):
        if self.session is None:
            self.client()
        return self.session.get(url, 
                                verify=False,
                                timeout=300
                                )
    
    def post_data(self, url, data):
        if self.session is None:
            self.client()
        
        return self.session.post(
            url,
            data=data,
            verify=False,
            timeout=300,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': self.get_random_user_agent(), 
            }
        )
        
        
    def post_json(self, url, json):
        if self.session is None:
            self.client()
        return self.session.post(
            url,
            verify=False,
            json=json,
            timeout=300,
        )
    
    def decode_email(self, encodedString):
        r = int(encodedString[:2],16)
        return ''.join(
            [
                chr(int(encodedString[i : i + 2], 16) ^ r)
                for i in range(2, len(encodedString), 2)
            ]
        )
        
        
        
class CauseGenerator:
    def _get_c_id(self, keyword, sensitivity):
        try:
            dictionary = None
            with open("approved_causes/data.json", "r") as f:
                dictionary = json.load(f)
            if not dictionary:
                raise NoDataError("No data found")
            best_ratio = 0
            best_category = None
            for category, id in dictionary.items():
                ratio = fuzz.token_set_ratio(keyword, category)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_category = id
            return None if best_ratio < sensitivity else best_category
        except Exception as e:
            return None
                     
    def format_list(self, lists):
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
    def reverse_list(self, string):
        return re.findall(r'"([^"]*)"', string)
    
    def generator_get_causes(self, causes:list, sensitivity:int = 40):
        if not causes:
            return None
        causes_id = [self._get_c_id(cause, sensitivity) for cause in causes]
        # remove None values
        causes_id = [x for x in causes_id if x]
        return self.format_list(causes_id)
    

class CleanData:
    def clean_text(self, text):
        return (
            clean(
                text,
                fix_unicode=True,
                to_ascii=True,
                no_line_breaks=True,
                no_urls=True,
                no_emails=True,
                no_phone_numbers=True,
                replace_with_url="",
                replace_with_phone_number="",
                no_emoji=True,
                normalize_whitespace=True
            )
            if text
            else ""
        )
        
    def clean_phone(self, phone):
        return clean(
            phone,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=True,
            no_phone_numbers=False,
            replace_with_url="",
            normalize_whitespace=True,
        )
    def clean_link(self, link):
        return clean(
            link,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=False,
            no_emails=True,
            no_phone_numbers=True,
        )
    def clean_number(self, number):
        return clean(
            number,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=True,
            no_phone_numbers=False,
        )
    
    def clean_emails(self, emails):
        return clean(
            emails,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=False,
            no_phone_numbers=True,
        )
    def clean_country(self, country):
        country = self.clean_text(country)
        if country in ["united states", "usa", "us", "u.s.a", "u.s", "u.s.a.", "u.s.","united state", 
                            "united states of america.", "united states of america"]:
            return "United States of America"
        elif country in ["united kingdom", "uk", "u.k", "u.k.", "u.k"]:
            return "United Kingdom"
        else:
            return country
        
        
class ImageDownloader:
    @retry(Exception, tries=2, delay=2)    
    def _download(self, image_url, file_path):
        proxy = "http://swxthcae-rotate:pm8t1rnfa0dc@p.webshare.io:80/"
        proxies = {
            "http": proxy,
            "https": proxy
        }
        res = requests.get(image_url, stream=True, proxies=proxies,timeout=180)
        if res.status_code != 200:
            raise NoDataError(f"Error downloading {image_url}: BAD RESPONSE")
        with open(file_path, "wb") as f:
            f.write(res.content)
        return 
    
    def _format_list(self, lists):
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
    
    def approved_ext(self, ext):
        return ext in ["jpg", "jpeg", "png", "gif"]
    
    def save_image(self, image_url, image_path, base_name):
        _image_url = image_url
        if not image_url.endswith(".jpg") or not image_url.endswith(".png") or not image_url.endswith(".jpeg") or not image_url.endswith(".gif"):    
            _image_url = image_url.split("?")[0]
        ext_name = _image_url.split(".")[-1]
        if not self.approved_ext(ext_name):
            ext_name = "png"
        image_uuid = uuid.uuid4()
        base_name = slugify(base_name)
        file_name = f"{base_name}_{image_uuid}.{ext_name}"
        if len(file_name) > 160:
            first_20_base_name = base_name[:50]
            file_name = f"{first_20_base_name}_{image_uuid}.{ext_name}"
        file_path = f"{image_path}{file_name}"
        try:
            self._download(image_url, file_path)
        except Exception as e:
            return None
        return file_name
    
    def download_images(self, images_links:list, image_path, base_name:str):
        images = [self.save_image(image_link, image_path, base_name) for image_link in images_links]
        images = [image for image in images if image]
        return self._format_list(images)
    
    
    
    
class Helper:
    def search_nested_dict(self, nested_dict, search_key):
        for key, value in nested_dict.items():
            if key == search_key:
                return value
            elif isinstance(value, dict):
                result = self.search_nested_dict(value, search_key)
                if result is not None:
                    return result
        return None

    def get_full_region_name(self, short_name:str) -> str:
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
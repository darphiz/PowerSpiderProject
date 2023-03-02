import json
import uuid
import requests
from contextlib import suppress
from ngo_scraper.loggers import gg_log
from ngo_scraper.requests import ProxyRequestClient
from .models import GlobalGivingIndexedUrl
from bs4 import BeautifulSoup
from lxml import etree
from fuzzywuzzy import fuzz
from cleantext import clean
from retry import retry



class NoDataError(Exception):
    pass

logger = gg_log()


class GlobalGivingScraper(ProxyRequestClient):
    def __init__(self, link) -> None:
        self.url = "https://www.globalgiving.org"
        self.model = GlobalGivingIndexedUrl 
        self.link = link
        self.detail_link = None
        self.data = {}
        self.image_path = "images/global_giving/"
        return super().__init__()
        
    @retry(Exception, tries=3, delay=2)    
    def _download(self, image_url, file_path):
        res = requests.get(image_url, stream=True)
        if res.status_code != 200:
            raise NoDataError(f"Error downloading {image_url}: BAD RESPONSE")
        with open(file_path, "wb") as f:
            f.write(res.content)
        return 
        
    def _save_image(self, image_url):
        ext_name = image_url.split(".")[-1]
        image_uuid = uuid.uuid4()
        file_name = f"{image_uuid}.{ext_name}"
        file_path = f"{self.image_path}{file_name}"
        try:
            self._download(image_url, file_path)
        except Exception as e:
            logger.error(f"Error saving image {image_url}: {str(e)}")
            return None
        return file_name
    
    def _populate_db(self):
        range_ = range(1, 8)   
        all_urls = []
        for data in range_:
            with open(f"./global_giving/{data}.txt", "r") as f:
                urls = f.readlines()
                for url in urls:
                    url = url.strip()
                    all_urls.append(url)
        for url in all_urls:
            self.model.objects.get_or_create(url=url)
        return
    
    
    def _patch_url(self, url=None):
        return f"{self.url}{url}" if url else f"{self.url}{self.link}"

    def _clean_text(self, text):
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
            )
            if text
            else ""
        )
        
    def _clean_phone(self, phone):
        return clean(
            phone,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=True,
            no_phone_numbers=False,
            replace_with_url="",
        )
    def _clean_link(self, link):
        return clean(
            link,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=False,
            no_emails=True,
            no_phone_numbers=True,
        )
    def _clean_number(self, number):
        return clean(
            number,
            fix_unicode=True,
            to_ascii=True,
            no_line_breaks=True,
            no_urls=True,
            no_emails=True,
            no_phone_numbers=False,
        )
    
    
    def _get_organization_name(self, page_tree):
        try:
            org_name_xpath = "/html/body/div[2]/div[1]/span[1]/a"
            org_name = page_tree.xpath(org_name_xpath)
            a_element = org_name[0]
            org_name_ = self._clean_text(a_element.text)
            if not org_name_:
                raise NoDataError("No organization name found")
            detail_link = a_element.attrib["href"]
            self.detail_link = self._patch_url(detail_link)
            return org_name_
        except Exception as e:
            logger.error(f"Error getting organization name -> {e}")
            raise e
    
    def _get_id(self, keyword):
        try:
            dictionary = None
            with open("pledge_app/data.json", "r") as f:
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
            return None if best_ratio < 30 else best_category
        except Exception as e:
            return None
                 
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
    
    def _get_org_addr(self, page_soup):
        with suppress(Exception):
            addr_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > div"
            addr = page_soup.select(addr_selector)
            addr = addr[0].text
            return self._clean_text(addr).title()    
        return ""

    def _get_country(self, page_soup):
        with suppress(Exception):
            country_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > div > span:nth-child(6)"
            country = page_soup.select(country_selector)
            country = country[0].text
            return self._clean_text(country).title()
        return ""
    
    def _get_state(self, page_soup):
        with suppress(Exception):
            state_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > div > span:nth-child(3)"
            state = page_soup.select(state_selector)
            state = state[0].text
            return self._clean_text(state).title()
        return ""
    
    def _get_causes(self, page_soup):
        with suppress(Exception):
            causes_container_div = "body > div:nth-child(2) > section:nth-child(5) > div > div > div.grid-parent.layout_center.js-projectsList > div > div.paginate_content.grid-parent.layout_center"
            causes_div = page_soup.select(causes_container_div)
            causes = causes_div[0].find_all("div", class_="grid-12 grid-ml-6 grid-lg-4 box_bottomMargin3 box_horizontalPadded1 js-project_tile project_tile")
            causes = [cause.find_all("a")[2].text for cause in causes]
            causes_id = [self._get_id(cause) for cause in causes]
            return self._format_list(causes_id)
        return None
    
    def _get_phone(self, page_soup):
        phone_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > span"
        phone = page_soup.select(phone_selector)
        return self._clean_phone(phone) if (phone := phone[0].text) else phone
    
    def _get_website(self, page_soup):
        with suppress(Exception):
            website_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div:nth-child(2) > a"
            website = page_soup.select(website_selector)
            # get the href attribute of the first element
            link = website[0].get("href")
            return self._clean_link(link)
        return ""
    
    def _get_mission(self, page_soup):
        mission_selector = "body > div:nth-child(2) > section:nth-child(4) > div > div > div.layout_alignLeft > p"
        mission = page_soup.select(mission_selector)
        return self._clean_text(mission[0].text) if mission else None

    def _get_description(self, page_soup):
        challenge = self._extract(
            "body > div.col_defaultBg.cuke-project > div.grid-padder.grid-parent.box_bottomPadded3 > div.grid-12.grid-md-6.grid-lg-8.box_padded1 > div.border_default.col_white.box_padded3.js-story > div.grid-0.grid-md-12.js-readMore > div.box_topMargin3 > p:nth-child(2)",
            page_soup,
        )
        solution = self._extract(
            "body > div.col_defaultBg.cuke-project > div.grid-padder.grid-parent.box_bottomPadded3 > div.grid-12.grid-md-6.grid-lg-8.box_padded1 > div.border_default.col_white.box_padded3.js-story > div.grid-0.grid-md-12.js-readMore > div.box_topMargin3 > p:nth-child(4)",
            page_soup,
        )
        return f"{challenge} {solution}"

    def _extract(self, arg0, page_soup):
        challenge_selector = arg0
        result = page_soup.select(challenge_selector)
        result = self._clean_text(result[0].text) if result else ""
        return result
        
    def _get_reg_year(self, page_soup):
        year_selector = "body > div:nth-child(2) > section:nth-child(4) > div > div > div.grid-parent.layout_center > div:nth-child(1) > div.text_fontSizeLarger.text_7n.col_ggPrimary3Text > span"
        year = page_soup.select(year_selector)
        return self._clean_number(year[0].text) if year else None
    
    def _scrape_image(self, page_soup):
        # sourcery skip: assign-if-exp, extract-duplicate-method, inline-immediately-returned-variable, introduce-default-else, move-assign-in-block
        thumb_img = None
        thumb_selector = "body > div:nth-child(2) > div.layout_rel.box_bottomMargin5 > div > img"
        if thumb := page_soup.select(thumb_selector):
            thumb = thumb[0].get("src")
            thumb = self._clean_link(thumb)
            thumb_img = self._save_image(thumb)
        cover_img = None


        cover_selector_div = "body > div:nth-child(2) > div.hero.layout_hideOverflow.grid-parent.layout_center.layout_noWrap"
        cover_selector = page_soup.select(cover_selector_div)
        # cover image is the third img in the div
        cover_selector = cover_selector[0].find_all("img")[2]
        cover = cover_selector.get("src")
        if cover := self._clean_link(cover):
            cover_img = self._save_image(cover)
        images = [thumb_img, cover_img]
        images = [image for image in images if image is not None]
        return images
    
    
    def scrape(self):
        response = self.query(self.detail_link)
        if response.status_code != 200:
            logger.error(f"Error scraping {self.detail_link} -> {response.status_code}")
            return
        page_soup = BeautifulSoup(response.content, "html.parser")
        self.data["organization_address"] = self._get_org_addr(page_soup)
        self.data["country"] = self._get_country(page_soup)
        self.data["state"] = self._get_state(page_soup)
        self.data["cause"] = self._get_causes(page_soup)        
        self.data["email"] = ""
        self.data["phone"] = self._get_phone(page_soup)
        self.data["website"] = self._get_website(page_soup)
        self.data["mission"] = self._get_mission(page_soup)
        self.data["govt_reg_number"] = ""
        self.data["govt_reg_number_type"] = ""
        self.data["registration_date_year"] = self._get_reg_year(page_soup)
        self.data["registration_date_month"] = ""
        self.data["registration_date_day"] = ""
        self.data["gross_income"] = ""
        self.data["image"] = self._format_list(self._scrape_image(page_soup))
        self.data["domain"] = self.url
        self.data["urls_scraped"] = self.detail_link
    
    def crawl(self):
        link = self._patch_url()
        response = self.query(link)
        if response.status_code != 200:    
            logger.error(f"Error crawling {link} -> {response.status_code}")
            return
        page_soup = BeautifulSoup(response.content, "html.parser")
        page_tree = etree.HTML(str(page_soup))
        self.data["organization_name"] = self._get_organization_name(page_tree).title()
        self.data["description"] = self._get_description(page_soup)
        self.scrape()
        return self.data
        
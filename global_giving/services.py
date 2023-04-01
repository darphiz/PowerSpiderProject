import logging
from contextlib import suppress
from ngo_scraper.requests import CauseGenerator, CleanData, Helper, ImageDownloader, ProxyRequestClient
from .models import GlobalGivingIndexedUrl
from bs4 import BeautifulSoup
from lxml import etree
from ngo_scraper.notification import Notify


class NoDataError(Exception):
    pass

logger = logging.getLogger(__name__)


class GlobalGivingScraper(
    ProxyRequestClient,     
    CauseGenerator, 
    CleanData,
    Notify,
    ImageDownloader,
    Helper
    ):
    def __init__(self, link) -> None:
        self.url = "https://www.globalgiving.org"
        self.model = GlobalGivingIndexedUrl 
        self.link = link
        self.detail_link = None
        self.data = {}
        self.image_path = "images/global_giving/"
        return super().__init__()
        
    
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

    
    def _get_organization_name(self, page_tree):
        try:
            org_name_xpath = "/html/body/div[2]/div[1]/span[1]/a"
            org_name = page_tree.xpath(org_name_xpath)
            a_element = org_name[0]
            org_name_ = self.clean_text(a_element.text)
            if not org_name_:
                raise NoDataError("No organization name found")
            detail_link = a_element.attrib["href"]
            self.detail_link = self._patch_url(detail_link)
            return org_name_
        except Exception as e:
            logger.error(f"Error getting detail page of organization -> {e}")
            with suppress(Exception):
                org_name_xpath = "/html/body/div[2]/div[1]/span[1]"
                org_name = page_tree.xpath(org_name_xpath)
                org = org_name[0].text
                # remove the "by" from the organization name
                org = org.lower()
                org = org.split("by")[1]
                return self.clean_text(org)
            raise NoDataError("No organization name found")

    

    def _get_org_addr(self, page_soup):
        with suppress(Exception):
            addr_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > div"
            addr = page_soup.select(addr_selector)
            addr = addr[0].text
            return self.clean_text(addr).title()    
        return ""

    def _get_country(self, page_soup):
        with suppress(Exception):
            if c_span := page_soup.find("span", itemprop="addressCountry"):
                country = c_span.text
                return self.clean_country(self.clean_text(country))
        return ""
    
    def _get_state(self, page_soup):
        with suppress(Exception):
            if state := page_soup.find("span", itemprop="addressRegion"):
                state = state.text
                return self.get_full_region_name(self.clean_text(state)).lower()
        return ""
    
    def _get_causes(self, page_soup):
        with suppress(Exception):
            causes_container_div = "body > div:nth-child(2) > section:nth-child(5) > div > div > div.grid-parent.layout_center.js-projectsList > div > div.paginate_content.grid-parent.layout_center"
            causes_div = page_soup.select(causes_container_div)
            causes = causes_div[0].find_all("div", class_="grid-12 grid-ml-6 grid-lg-4 box_bottomMargin3 box_horizontalPadded1 js-project_tile project_tile")
            causes = [cause.find_all("a")[2].text for cause in causes]
            return self.generator_get_causes(causes)
        return None
            
    
    def _get_phone(self, page_soup):
        with suppress(Exception):
            phone_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div.box_topPadded2 > span"
            phone = page_soup.select(phone_selector)
            return self.clean_phone(phone) if (phone := phone[0].text) else phone
        return None
    
    
    def _get_website(self, page_soup):
        with suppress(Exception):
            website_selector = "body > div:nth-child(2) > section.layout_center.org_map.col_defaultBg.layout_rel > div > div > div.grid-0.grid-lg-12.org_info_overlay.layout_abs.layout_abs_leftInner.org_info_overlay_centerVertical.layout_alignLeft.border_default.col_white.box_verticalPadded3.box_horizontalPadded2 > div:nth-child(2) > a"
            website = page_soup.select(website_selector)
            # get the href attribute of the first element
            link = website[0].get("href")
            return self.clean_link(link)
        return ""
    
    def _get_mission(self, page_soup):
        mission_selector = "body > div:nth-child(2) > section:nth-child(4) > div > div > div.layout_alignLeft > p"
        mission = page_soup.select(mission_selector)
        return self.clean_text(mission[0].text) if mission else None

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
        result = self.clean_text(result[0].text) if result else ""
        return result
        
    def _get_reg_year(self, page_soup):
        year_selector = "body > div:nth-child(2) > section:nth-child(4) > div > div > div.grid-parent.layout_center > div:nth-child(1) > div.text_fontSizeLarger.text_7n.col_ggPrimary3Text > span"
        year = page_soup.select(year_selector)
        return self.clean_number(year[0].text) if year else None
    
    def _scrape_image(self, page_soup):
        with suppress(Exception):
            thumb_img = None
            thumb_selector = "body > div:nth-child(2) > div.layout_rel.box_bottomMargin5 > div > img"
            if thumb := page_soup.select(thumb_selector):
                thumb = thumb[0].get("src")
                thumb = self.clean_link(thumb)
                thumb_img = thumb


            cover_selector_div = "body > div:nth-child(2) > div.hero.layout_hideOverflow.grid-parent.layout_center.layout_noWrap"
            cover_selector = page_soup.select(cover_selector_div)
            # cover image is the third img in the div
            try:
                c_selector = cover_selector[0].find_all("img")[2]
            except IndexError:
                c_selector = cover_selector[0].find_all("img")[0]
            cover = c_selector.get("src")
            cover_img = cover if (cover := self.clean_link(cover)) else None
            images = [thumb_img, cover_img]
            images = [image for image in images if image is not None]

            return self.download_images(images, self.image_path, self.data["organization_name"])
        return None
    
    def scrape(self):
        response = self.query(self.detail_link)
        if response.status_code != 200:
            logger.error(f"Error scraping {self.detail_link} -> {response.status_code}")
            return
        page_soup = BeautifulSoup(response.content, "html.parser")
        self.data["organization_address"] = self.clean_text(self._get_org_addr(page_soup))
        self.data["country"] = self._get_country(page_soup)
        self.data["state"] = self._get_state(page_soup)
        self.data["cause"] = self._get_causes(page_soup)        
        self.data["email"] = ""
        self.data["phone"] = self._get_phone(page_soup)
        self.data["website"] = self._get_website(page_soup)
        self.data["mission"] = self.clean_text(self._get_mission(page_soup))
        self.data["govt_reg_number"] = ""
        self.data["govt_reg_number_type"] = ""
        self.data["registration_date_year"] = self._get_reg_year(page_soup)
        self.data["registration_date_month"] = ""
        self.data["registration_date_day"] = ""
        self.data["gross_income"] = ""
        self.data["image"] = self._scrape_image(page_soup)
        self.data["domain"] = self.format_list([self.url,])
        self.data["urls_scraped"] = self.format_list([self.detail_link,])
    
    def crawl(self):
        link = self._patch_url()
        response = self.query(link)
        if response.status_code != 200:    
            logger.error(f"Error crawling {link} -> {response.status_code}")
            return
        page_soup = BeautifulSoup(response.content, "html.parser")
        page_tree = etree.HTML(str(page_soup))
        self.data["organization_name"] = self.clean_text(self._get_organization_name(page_tree))
        self.data["description"] = self.clean_text(self._get_description(page_soup))
        if not self.data["organization_name"]:
            logger.error(f"Error crawling {link} -> organization name not found")
            return
        if not self.detail_link:
            self.data["domain"] = self.format_list([self.url,])
            self.data["urls_scraped"] = self.format_list([link,])
            return self.data

        self.scrape()
        return self.data
        
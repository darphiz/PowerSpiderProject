import logging
from bs4 import BeautifulSoup
from ngo_scraper.notification import Notify
from ngo_scraper.requests import CleanData, CauseGenerator, ProxyRequestClient
from django.conf import settings
import urllib.parse


logger = logging.getLogger(__name__)
HOOK = settings.FRCA_HOOK
class FCRA_Scraper(ProxyRequestClient, CauseGenerator, CleanData, Notify):
    def __init__(self, state_name, state_id, state_year) -> None:
        self.root_url = "https://fcraonline.nic.in/fc8_statewise.aspx"
        self.state_name = state_name
        self.state_id = state_id
        self.state_year = state_year
        self.webhook_url = HOOK
        return super().__init__()
    
    def string_to_list(self, s):
        return s.split(',') if s else []
    
    def parse_html_table(self, html_string):
        soup = BeautifulSoup(html_string, 'html.parser')
        table = soup.find('table', class_='table table-responsive table-bordered gridview info_bank')
        rows = table.find_all('tr')[1:]

        data = []
        for row in rows:
            cols = row.find_all('td')
            registration_no = cols[1].text.strip()
            association_name = cols[2].text.strip()
            address = cols[3].text.strip()
            nature = self.string_to_list(cols[4].text.strip())
            data.append(
                    {
                        'govt_reg_number': self.clean_number(registration_no), 
                        'organization_name': self.clean_text(association_name), 
                        'organization_address': self.clean_text(address), 
                        'cause': self.generator_get_causes(nature),
                        'state': self.clean_text(self.state_name),
                        'country': 'India',
                        'govt_reg_number_type': 'FRCA',
                        'domain': self.format_list(["https://fcraonline.nic.in/", ]),
                        'urls_scraped': self.format_list(["https://fcraonline.nic.in/fc8_statewise.aspx", ])
                    }
            )
        return data

    def crawl(self):
        view_state="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"
        view_state_generator="CB73C42E"
        year=self.state_year
        state=self.state_id
        form_data = f"__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={urllib.parse.quote(view_state)}&__VIEWSTATEGENERATOR={view_state_generator}&__VIEWSTATEENCRYPTED=&h_hash=&h_hash_retype=&ddl_year_tbl0={year}&ddl_state_tbl0={state}&btn_tbl0_submit=Submit&ddlstate=0&ddldist=0&txtseaShow more"
        data = self.post_data(
            self.root_url,
            data=form_data
        )
        if data.status_code != 200:
            logger.error(f"Error: Unable to work on {self.state_name} -{self.state_year}")
            self.alert(Notify.error(f"Error: Unable to work on {self.state_name} -{self.state_year}"))
            return None
        try:
            parsed_data = self.parse_html_table(data.text)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            self.alert(Notify.error(f"Error: {str(e)}"))
            return None
        return parsed_data
from contextlib import suppress
import requests
import zipfile
import lxml
from bs4 import BeautifulSoup

from ngo_scraper.requests import CauseGenerator
from .models import XML_NGO, XMLUrlIndexer
from django.db import transaction
from .utils import us_state_to_abbrev
import xmltodict


class XMLUrlSpider:
    """
    Download the IRS 990 XML files from the IRS website
    No need to use Proxy
    """
    def __init__(self):
        self.endpoint = "https://www.irs.gov/charities-non-profits/form-990-series-downloads"
        self.xml_urls = []

    def get_xml_urls(self):
        s = requests.Session()
        page = s.get(self.endpoint)
        soup = BeautifulSoup(page.content, "html.parser")
        zip_urls = []
        for list_item in soup.find_all("li"):
            if list_item.find('a'):
                if href := list_item.find('a').get("href"):
                    if "download990xml" in href and href.endswith(".zip"):
                        zip_urls.append(href)
        zip_urls.sort()
        self.xml_urls = list(zip_urls)
        return self.xml_urls
    
    def index_zip_urls(self):
        self.get_xml_urls()
        for url in self.xml_urls:
            try:
                with transaction.atomic():
                    XMLUrlIndexer.objects.create(url=url)
            except Exception as e:
                print(e)
                continue
        return self.xml_urls
    
    def get_indexed_urls(self):
        return [url.url for url in XMLUrlIndexer.objects.all()]

    @staticmethod
    def download_xml_file(url):
        try:
            url_obj = XMLUrlIndexer.objects.get(url=url)
        except XMLUrlIndexer.DoesNotExist:
            print("Url not indexed")
        endpoint = url
        try:
            zip_name = f"irs_app/irs_xml/{url_obj.file_name}.zip"
            print(f"Downloading {zip_name}...")
            with requests.get(endpoint, stream=True) as r:
                r.raise_for_status()
                with open(zip_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size = 65536): 
                        f.write(chunk)
            print(f"Downloaded {url_obj.file_name}.zip.")
            url_obj.is_downloaded = True
            url_obj.locked = False
            url_obj.save()
        except Exception as e:  
            print(e)
            url_obj.locked = False
            url_obj.trial += 1
            url_obj.save()
            return
        
        
        
class XMLScraper(CauseGenerator):
    """
    Scrape the XML files and save the data
    """
    def __init__(self, url):
        self.url = url
        return super().__init__()    
        
    def _get_org_mission(self, parsed_xml):
        with suppress(Exception):
            org_mission = parsed_xml["Return"]["ReturnData"]["IRS990EZ"]["ProgramSrvcAccomplishmentGrp"]["DescriptionProgramSrvcAccomTxt"]
            return org_mission.lower()
        return ""
     
    def _get_total_revenue(self, parsed_xml):
        with suppress(Exception):
            return parsed_xml["Return"]["ReturnData"]["IRS990EZ"]["TotalRevenueAmt"]
        return ""
     
     
    def process_xml_file(self, xml_name, memorybuffer):
        root = lxml.etree.XML(memorybuffer)
        abbrev_to_us_state = dict(map(reversed, us_state_to_abbrev.items()))
        root = lxml.etree.XML(memorybuffer)
        parsed_xml = xmltodict.parse(memorybuffer)
        ns = {"ns": "http://www.irs.gov/efile"}
        organization_mission = self._get_org_mission(parsed_xml)
        total_revenue = self._get_total_revenue(parsed_xml)
        
        state = ""
        non_profit_address = ""
        country = ""
        tax_preparer_full_name = ""
        tax_preparer_first_name = ""
        tax_preparer_last_name = ""
        tax_preparer_email = ""
        tax_preparer_phone_number = ""
        non_profit_full_name = ""
        non_profit_first_name = ""
        non_profit_last_name = ""
        non_profit_email = ""
        non_profit_phone_number = ""
        website = ""
        ein = ""

        if len(root.xpath('//ns:Filer/ns:BusinessName/ns:BusinessNameLine1Txt', namespaces=ns)) > 0:
            organization_name = root.xpath('//ns:Filer/ns:BusinessName/ns:BusinessNameLine1Txt', namespaces=ns)[0].text
        elif len(root.xpath('//ns:Filer/ns:BusinessName/ns:BusinessNameLine1', namespaces=ns)) > 0:
            organization_name = root.xpath('//ns:Filer/ns:BusinessName/ns:BusinessNameLine1', namespaces=ns)[0].text
        elif len(root.xpath('//ns:Filer/ns:Name/ns:BusinessNameLine1', namespaces=ns)) > 0:
            organization_name = root.xpath('//ns:Filer/ns:Name/ns:BusinessNameLine1', namespaces=ns)[0].text

        usaddress = root.xpath('//ns:Filer/ns:USAddress', namespaces=ns)
        foreign_address = root.xpath('//ns:Filer/ns:ForeignAddress', namespaces=ns)
        if len(usaddress) > 0:
            if len(usaddress[0].xpath('ns:StateAbbreviationCd', namespaces=ns)) > 0:
                state = usaddress[0].xpath('ns:StateAbbreviationCd', namespaces=ns)[0].text
            elif len(usaddress[0].xpath('ns:State', namespaces=ns)) > 0:
                state = usaddress[0].xpath('ns:State', namespaces=ns)[0].text

            if len(usaddress[0].xpath('ns:AddressLine1Txt', namespaces=ns)) > 0:
                non_profit_address = usaddress[0].xpath('ns:AddressLine1Txt', namespaces=ns)[0].text
            elif len(usaddress[0].xpath('ns:AddressLine1', namespaces=ns)) > 0:
                non_profit_address = usaddress[0].xpath('ns:AddressLine1', namespaces=ns)[0].text

            if len(usaddress[0].xpath('ns:CityNm', namespaces=ns)) > 0:
                non_profit_address += ", " + usaddress[0].xpath('ns:CityNm', namespaces=ns)[0].text
            elif len(usaddress[0].xpath('ns:City', namespaces=ns)) > 0:
                non_profit_address += ", " + usaddress[0].xpath('ns:City', namespaces=ns)[0].text

            non_profit_address += ", " + state

            if len(usaddress[0].xpath('ns:ZIPCd', namespaces=ns)) > 0:
                non_profit_address += ", " + usaddress[0].xpath('ns:ZIPCd', namespaces=ns)[0].text
            elif len(usaddress[0].xpath('ns:ZIPCode', namespaces=ns)) > 0:
                non_profit_address += ", " + usaddress[0].xpath('ns:ZIPCode', namespaces=ns)[0].text

            country = "united states of america"

        elif len(foreign_address) > 0:
            if len(foreign_address[0].xpath('ns:ProvinceOrStateNm', namespaces=ns)) > 0:
                state = foreign_address[0].xpath('ns:ProvinceOrStateNm', namespaces=ns)[0].text
            elif len(foreign_address[0].xpath('ns:ProvinceOrState', namespaces=ns)) > 0:
                state = foreign_address[0].xpath('ns:ProvinceOrState', namespaces=ns)[0].text

            if len(foreign_address[0].xpath('ns:AddressLine1Txt', namespaces=ns)) > 0:
                non_profit_address = foreign_address[0].xpath('ns:AddressLine1Txt', namespaces=ns)[0].text
            elif len(foreign_address[0].xpath('ns:AddressLine1', namespaces=ns)) > 0:
                non_profit_address = foreign_address[0].xpath('ns:AddressLine1', namespaces=ns)[0].text

            if len(foreign_address[0].xpath('ns:CityNm', namespaces=ns)) > 0:
                non_profit_address += ", " + foreign_address[0].xpath('ns:CityNm', namespaces=ns)[0].text
            elif len(foreign_address[0].xpath('ns:City', namespaces=ns)) > 0:
                non_profit_address += ", " + foreign_address[0].xpath('ns:City', namespaces=ns)[0].text

            if state:
                non_profit_address += ", " + state

            if len(foreign_address[0].xpath('ns:ForeignPostalCd', namespaces=ns)) > 0:
                non_profit_address += ", " + foreign_address[0].xpath('ns:ForeignPostalCd', namespaces=ns)[0].text
            elif len(foreign_address[0].xpath('ns:PostalCode', namespaces=ns)) > 0:
                non_profit_address += ", " + foreign_address[0].xpath('ns:PostalCode', namespaces=ns)[0].text

            if len(foreign_address[0].xpath('ns:CountryCd', namespaces=ns)) > 0:
                country = foreign_address[0].xpath('ns:CountryCd', namespaces=ns)[0].text
            elif len(foreign_address[0].xpath('ns:Country', namespaces=ns)) > 0:
                country = foreign_address[0].xpath('ns:Country', namespaces=ns)[0].text

        if len(root.xpath('//ns:PreparerPersonGrp/ns:PreparerPersonNm', namespaces=ns)) > 0:
            tax_preparer_full_name = root.xpath('//ns:PreparerPersonGrp/ns:PreparerPersonNm', namespaces=ns)[0].text 
            names = tax_preparer_full_name.split(" ")  
            tax_preparer_first_name = names[0]
            tax_preparer_last_name = names[-1] if len(names) > 1 else ""

        if len(root.xpath('//ns:PreparerPersonGrp/ns:PhoneNum', namespaces=ns)) > 0:
            phone_number = root.xpath('//ns:PreparerPersonGrp/ns:PhoneNum', namespaces=ns)[0].text 
            tax_preparer_phone_number = "+1 " + phone_number[0:3] + " " + phone_number[3:6] + " " + phone_number[6:]

        if len(root.xpath('//ns:BusinessOfficerGrp/ns:PersonNm', namespaces=ns)) > 0:
            non_profit_full_name = root.xpath('//ns:BusinessOfficerGrp/ns:PersonNm', namespaces=ns)[0].text 
            names = non_profit_full_name.split(" ")  
            non_profit_first_name = names[0]
            non_profit_last_name = names[-1] if len(names) > 1 else ""

        if len(root.xpath('//ns:BusinessOfficerGrp/ns:PhoneNum', namespaces=ns)) > 0:
            phone_number = root.xpath('//ns:BusinessOfficerGrp/ns:PhoneNum', namespaces=ns)[0].text 
            non_profit_phone_number = "+1 " + phone_number[0:3] + " " + phone_number[3:6] + " " + phone_number[6:]

        website_node = root.xpath('//ns:ReturnData/ns:IRS990EZ/ns:WebsiteAddressTxt', namespaces=ns)
        if len(website_node) > 0:
            website = website_node[0].text

        ein_node = root.xpath('//ns:Filer/ns:EIN', namespaces=ns)
        if len(ein_node) > 0:
            ein = ein_node[0].text.replace(" ","").replace("-","")

        achievement = ["","","","",""]
        achievement_nodes = root.xpath('//ns:ProgramSrvcAccomplishmentGrp/ns:DescriptionProgramSrvcAccomTxt', namespaces=ns)
        if len(achievement_nodes) > 0:
            achievement[0] = achievement_nodes[0].text
        if len(achievement_nodes) > 1:
            achievement[1] = achievement_nodes[1].text
        if len(achievement_nodes) > 2:
            achievement[2] = achievement_nodes[2].text
        if len(achievement_nodes) > 3:
            achievement[3] = achievement_nodes[3].text
        if len(achievement_nodes) > 4:
            achievement[4] = achievement_nodes[4].text  

        achievement_cost = ["","","","",""]
        achievement_cost_nodes = root.xpath('//ns:ProgramSrvcAccomplishmentGrp/ns:ProgramServiceExpensesAmt', namespaces=ns)
        if len(achievement_cost_nodes) > 0:
            achievement_cost[0] = achievement_cost_nodes[0].text
        if len(achievement_cost_nodes) > 1:
            achievement_cost[1] = achievement_cost_nodes[1].text
        if len(achievement_cost_nodes) > 2:
            achievement_cost[2] = achievement_cost_nodes[2].text
        if len(achievement_cost_nodes) > 3:
            achievement_cost[3] = achievement_cost_nodes[3].text
        if len(achievement_cost_nodes) > 4:
            achievement_cost[4] = achievement_cost_nodes[4].text

        if len(root.xpath('//ns:ReturnTypeCd', namespaces=ns)) > 0:
            return_type = root.xpath('//ns:ReturnTypeCd', namespaces=ns)[0].text
        else:
            return_type = root.xpath('//ns:ReturnType', namespaces=ns)[0].text

        if len(root.xpath('//ns:TaxPeriodBeginDt', namespaces=ns)) > 0:
            tax_period_start = root.xpath('//ns:TaxPeriodBeginDt', namespaces=ns)[0].text
        else:
            tax_period_start = root.xpath('//ns:TaxPeriodBeginDate', namespaces=ns)[0].text

        if len(root.xpath('//ns:TaxPeriodEndDt', namespaces=ns)) > 0:
            tax_period_end = root.xpath('//ns:TaxPeriodEndDt', namespaces=ns)[0].text
        else:
            tax_period_end = root.xpath('//ns:TaxPeriodEndDate', namespaces=ns)[0].text

        data = (
            organization_name,
            non_profit_address, 
            country, 
            abbrev_to_us_state[state] if state in abbrev_to_us_state else state,         
            tax_preparer_full_name, 
            tax_preparer_first_name, 
            tax_preparer_last_name, 
            tax_preparer_email, 
            tax_preparer_phone_number, 
            non_profit_full_name,
            non_profit_first_name,
            non_profit_last_name,
            non_profit_email, 
            non_profit_phone_number, 
            website, 
            ein, 
            achievement[0], 
            achievement_cost[0], 
            achievement[1], 
            achievement_cost[1],
            achievement[2], 
            achievement_cost[2],
            achievement[3], 
            achievement_cost[3],
            achievement[4], 
            achievement_cost[4],
            return_type,
            tax_period_start,
            tax_period_end,
            xml_name)
        
        
        irs_data = {}
        irs_data["organization_name"] = (data[0] or "").lower()
        irs_data["organization_address"] = (data[1] or "").lower()
        irs_data["country"] = (data[2] or "").lower()
        irs_data["state"] = (data[3] or "").lower()
        irs_data["email"] = (data[7] or "").lower()
        irs_data["mission"] = (organization_mission or "").lower()
        irs_data["govt_reg_number"] = (data[15] or "").lower()
        irs_data["govt_reg_number_type"] = "EIN"
        irs_data["gross_income"] = (total_revenue or "").lower()
        irs_data["domain"] = self.format_list(["https://irs.gov"])
        irs_data["urls_scraped"] = self.format_list([self.url])
        return irs_data
        
    def scrape(self):
        try:
            url_obj = XMLUrlIndexer.objects.get(url=self.url)
        except XMLUrlIndexer.DoesNotExist:
            print("Url not indexed")
            return
        
        zip_name = f"irs_app/irs_xml/{url_obj.file_name}.zip"
        with zipfile.ZipFile(zip_name, "r") as input_zip:
            print(f"Processing {zip_name}")
            xml_list = input_zip.namelist()
            total = len(xml_list)
            for index in range(total):
                xml_name = xml_list[index]
                memorybuffer = input_zip.read(xml_name)
                xml_data = self.process_xml_file(xml_name, memorybuffer)
                if xml_data:
                    try:
                        with transaction.atomic():
                            XML_NGO.objects.create(**xml_data)    
                    except Exception as e:
                        print(e)                        
                if index == 200:
                    break
                print(f"Processed {index+1} of {total} files")
        return total
    
            
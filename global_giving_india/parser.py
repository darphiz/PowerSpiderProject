import PyPDF2
import re

class RetrieveLinks:
    def __init__(self, file):
        self.file = file
        self.links = []
                
    def _extract_links(self, text):
       url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
       return re.findall(url_pattern, text)
    
    def crawl_file(self):
        with open(self.file, 'rb') as file:
            readPDF = PyPDF2.PdfFileReader(file)
            for page_no in range(readPDF.numPages):
                page=readPDF.getPage(page_no)
                text = page.extractText()
                urls_in_page = self._extract_links(text)
                urls_in_page.remove('https://guidestarindia.org/CertifiedNGOs.aspx')
                self.links.extend(urls_in_page)

        return list(set(self.links))
        
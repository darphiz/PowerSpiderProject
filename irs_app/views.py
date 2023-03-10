from django.views import View
from django.shortcuts import HttpResponse
from irs_app.xml_services import XMLScraper, XMLUrlSpider
# from .tasks import xml_task_orchestrator

class IrsView(View):
    def get(self, request):
        """
        Do not call this view directly, for testing purposes only
        """
        # https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_8.zip
        # xml_task_orchestrator.delay()
        url = "https://apps.irs.gov/pub/epostcard/990/xml/2019/download990xml_2019_8.zip"
        # XMLUrlSpider.download_xml_file(url)
        XMLScraper(url).scrape()
        return HttpResponse("Starts indexing urls")
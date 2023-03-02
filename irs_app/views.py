from django.views import View
from django.shortcuts import HttpResponse
from irs_app.xml_services import XMLScraper
from .tasks import xml_task_orchestrator

class IrsView(View):
    def get(self, request):
        """
        Do not call this view directly, for testing purposes only
        """
        xml_task_orchestrator.delay()
        return HttpResponse("Starts indexing urls")
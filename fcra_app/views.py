from django.shortcuts import HttpResponse 
from django.views.generic import View

from fcra_app.services import FCRA_Scraper


class FCRAView(View):
    def get(self, request):
        scraper = FCRA_Scraper(
            state_name = "Delhi", 
            state_id = "23", 
            state_year="2015"
        )
        scraper.crawl()
        return HttpResponse("Ok")
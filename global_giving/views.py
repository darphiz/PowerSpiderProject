from django.views.generic import View
from django.http import HttpResponse
# from .tasks import scrape_global_giving
from .services import GlobalGivingScraper

class GGView(View):
    def get(self, request, *args, **kwargs):
        url = "/projects/empower-and-educate-wiser-girls-in-kenya/"
        print(
            GlobalGivingScraper(url).crawl()
        )
        return  HttpResponse("Hello World")



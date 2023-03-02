from django.views.generic import View
from django.http import HttpResponse
from .tasks import scrape_global_giving
class GGView(View):
    def get(self, request, *args, **kwargs):
        url = "/projects/relief-to-victims-of-floods/"
        scrape_global_giving.delay(url)
        return  HttpResponse("Hello World")



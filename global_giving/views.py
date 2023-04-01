from django.views.generic import View
# from .tasks import scrape_global_giving
from .services import GlobalGivingScraper
from django.http import JsonResponse

class GGView(View):
    def get(self, request, *args, **kwargs):
        url = "/microprojects/restore-acosmetics-shop-that-caught-fire-in-uganda/"
        
        data = GlobalGivingScraper(url).crawl()
        
        return JsonResponse(data, safe=False) 



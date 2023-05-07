from django.views.generic import View
# from .tasks import scrape_global_giving
from .services import GlobalGivingScraper
from django.http import JsonResponse

class GGView(View):
    def get(self, request, *args, **kwargs):
        url = "https://www.globalgiving.org/donate/68515/kenyan-network-of-cancer-organizations-kenco/"
        data = GlobalGivingScraper().scrape(url, scrape_images=False)
        return JsonResponse(data, safe=False) 




from django.http import JsonResponse
from django.views import View

from global_giving_india.services import GG_India_Scraper
# from global_giving_india.services import GG_India_Scraper
# from .tasks import scrape_ggi_data


class GGIndiaView(View):
    def get(self, request):
        "DO NOT RUN THIS CODE; FOR DEMO PURPOSES ONLY"
        spider = GG_India_Scraper("https://guidestarindia.org/Summary.aspx?CCReg=3554")
        data = spider.scrape()
        return JsonResponse(
            data, safe=False
        )
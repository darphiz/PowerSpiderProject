from django.shortcuts import HttpResponse
from django.views import View
from guidestar_app.services import GuideStarScraper
# from .tasks import scrape_guidestar_data


class GuideStarView(View):
    def get(self, request):
        spider = GuideStarScraper("/profile/41-2145557")
        print(spider.scrape())
        return HttpResponse("Hello World")


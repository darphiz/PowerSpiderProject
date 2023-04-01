from django.shortcuts import HttpResponse
from django.views import View
from guidestar_app.services import GuideStarScraper
# from .tasks import scrape_guidestar_data


class GuideStarView(View):
    def get(self, request):
        spider = GuideStarScraper("/profile/38-3722092", initial_data={"organization_name": "Test"})
        print(spider.scrape())
        return HttpResponse("Hello World")


from django.shortcuts import HttpResponse
from django.views import View
from guidestar_app.services import GuideStarScraper
from .tasks import scrape_guidestar_data


class GuideStarView(View):
    def get(self, request):
        scrape_guidestar_data.delay(url="/profile/39-1837860")
        return HttpResponse("Hello World")


from django.http import JsonResponse
from django.views import View
from django.conf import settings

from ngo_scraper.notification import Notify
from pledge_app.services import PledgeScraper

HOOK = settings.PLEDGE_HOOK
class StatusView(View):
    def get(self, request):
        data = PledgeScraper("/organizations/82-1776810/ipittythebull-foundation").scrape()
        
        return JsonResponse(data, safe=False)

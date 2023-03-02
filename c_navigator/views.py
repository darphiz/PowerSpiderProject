from django.http import HttpResponse
from django.views import View
from .services import CharityNavigatorScraper


class CharityView(View):
    def get(self, request):
        spider = CharityNavigatorScraper(1)
        data = spider.get_other_data(
            "https://www.charitynavigator.org/ein/521257057",
            ""
        )
        print(data)
        return HttpResponse("Hello World")
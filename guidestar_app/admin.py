from django.contrib import admin
from .models import GuideStarIndexedUrl, CrawlCursor, NGO

admin.site.register(GuideStarIndexedUrl)
admin.site.register(CrawlCursor)
admin.site.register(NGO)
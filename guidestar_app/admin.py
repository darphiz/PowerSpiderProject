from django.contrib import admin
from .models import GuideStarIndexedUrl, CrawlCursor, NGO,LastPage, ErrorPage

def remove_scraped(modeladmin, request, queryset):
    queryset.update(is_scraped=False, locked=False, trial=0)

class NGOAdmin(admin.ModelAdmin):
    search_fields = ["mission", "organization_name"]
    list_display = ["organization_name", "email"]


class URLIndexAdmin(admin.ModelAdmin):
    list_display = ["url", "is_scraped", "scraped_on", "trial"]
    list_filter = ["is_scraped", "locked", "trial"]
    search_fields = ["url"]
    actions = [remove_scraped,]    

admin.site.register(GuideStarIndexedUrl, URLIndexAdmin)
admin.site.register(CrawlCursor)
admin.site.register(NGO, NGOAdmin)
admin.site.register(LastPage)
admin.site.register(ErrorPage)
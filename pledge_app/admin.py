from django.contrib import admin
from .models import PledgeIndexedUrl, CrawlCursor, NGO,Cause



def remove_scraped(_, __, queryset):
    queryset.update(is_scraped=False, locked=False, trial=0)
remove_scraped.short_description = "Remove Scraped"



class IndexUrlAdmin(admin.ModelAdmin):
    list_display = ["url","is_scraped", "locked", "trial"]
    list_filter = ["is_scraped", "locked", "trial"]
    search_fields = ["url"]
    actions = [remove_scraped]
    

admin.site.register(CrawlCursor)
admin.site.register(PledgeIndexedUrl, IndexUrlAdmin)



    
admin.site.register(NGO)
admin.site.register(Cause)

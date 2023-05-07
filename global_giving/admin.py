from django.contrib import admin
from .models import GlobalGivingIndexedUrl, NGO

def unScrape(modeladmin, request, queryset):
    queryset.update(is_scraped=False, locked=False, trial=0)

class GlobalGivingIndexedUrlAdmin(admin.ModelAdmin):
    list_display = ['url', 'is_scraped', 'locked', 'trial']
    list_filter = ['is_scraped', 'locked', 'trial']
    search_fields = ['url']
    actions = [unScrape, ]
    


class NGOAdmin(admin.ModelAdmin):
    search_fields = ['organization_name', 'organization_address']


class NGOAdminV2(admin.ModelAdmin):
    search_fields = ['organization_name', 'organization_address']


admin.site.register(GlobalGivingIndexedUrl, GlobalGivingIndexedUrlAdmin)
admin.site.register(NGO, NGOAdminV2)
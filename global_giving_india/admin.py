from django.contrib import admin
from . models import GuideStarIndiaIndexedUrl, NGO


def unlock(_, __, queryset):
    queryset.update(locked=False, trial=0, is_scraped=False)

class GGIAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_scraped', 'locked', 'trial', 'scraped_on')
    list_filter = ('is_scraped', 'locked')
    search_fields = ('url',)
    actions = [unlock, ]

class NGOAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'organization_address', 'cause', 'website')


admin.site.register(GuideStarIndiaIndexedUrl, GGIAdmin)
admin.site.register(NGO, NGOAdmin)
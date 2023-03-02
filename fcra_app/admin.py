from django.contrib import admin
from .models import FCR_Cursor, FCR_NGO


def unScrape(_, __, queryset):
    queryset.update(is_scraped=False, locked=False)

unScrape.short_description = "Un-Scrape selected rows"


class CursorAdmin(admin.ModelAdmin):
    list_display = ('state', 'year', 'is_scraped', 'locked')
    actions = [unScrape, ]
    list_filter = ('state', 'year', 'is_scraped', 'locked')
class NGOAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'state', 'cause', 'website')
    list_filter = ('state', )
    search_fields = ('organization_name', 'state', 'website')

admin.site.register(FCR_Cursor, CursorAdmin)
admin.site.register(FCR_NGO, NGOAdmin)
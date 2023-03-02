from django.contrib import admin
from .models import CrawlCursor, NGO, FailedPages
# Register your models here.

class CrawlCursorAdmin(admin.ModelAdmin):
    list_display = ('app', 'current_page', 'max_cursor')


class NGOAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'state', 'cause')
    search_fields = ('organization_name', 'state')
    
admin.site.register(CrawlCursor, CrawlCursorAdmin)
admin.site.register(NGO, NGOAdmin)
admin.site.register(FailedPages)
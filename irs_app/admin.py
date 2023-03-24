from django.contrib import admin
from .models import (IRSIndexedUrl, 
                     LineMarker, 
                     NGO, 
                     XMLUrlIndexer,
                    )

def remove_scraped(_, __, queryset):
    queryset.update(is_scraped=False, scraped_on=None, locked=False)



class XMlURLIndexerAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_scraped', 'scraped_on', 'locked', 'trial', 'file_name')
    list_filter = ('is_scraped', 'locked', 'trial', "is_downloaded")
    search_fields = ('url',)
    

class IRSIndexedUrlAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_scraped', 'scraped_on', 'locked', 'trial')
    list_filter = ('is_scraped', 'locked', 'trial',)
    search_fields = ('url',)
    actions = [remove_scraped, ]

admin.site.register(NGO)
admin.site.register(LineMarker)
admin.site.register(XMLUrlIndexer, XMlURLIndexerAdmin)
admin.site.register(IRSIndexedUrl, IRSIndexedUrlAdmin)

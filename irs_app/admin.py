from django.contrib import admin
from .models import (IRSIndexedUrl, 
                     NGO, 
                     XMLUrlIndexer,
                     ZIP_NGO,
                     NGO_V2
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
class NGOAdmin(admin.ModelAdmin):
    list_filter = ("domain","country" )

admin.site.register(NGO, NGOAdmin)
admin.site.register(NGO_V2, NGOAdmin)

admin.site.register(XMLUrlIndexer, XMlURLIndexerAdmin)
admin.site.register(IRSIndexedUrl, IRSIndexedUrlAdmin)
admin.site.register(ZIP_NGO)
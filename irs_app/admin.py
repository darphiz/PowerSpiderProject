from django.contrib import admin
from .models import (IRSIndexedUrl, 
                     LineMarker, 
                     NGO, 
                     XMLUrlIndexer,
                     XML_NGO
                    )

class XMlURLIndexerAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_scraped', 'scraped_on', 'locked', 'trial')
    list_filter = ('is_scraped', 'locked', 'trial', "is_downloaded")
    search_fields = ('url',)



admin.site.register(IRSIndexedUrl)
admin.site.register(LineMarker)
admin.site.register(NGO)
admin.site.register(XMLUrlIndexer, XMlURLIndexerAdmin)
admin.site.register(XML_NGO)
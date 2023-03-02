from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pledge/', include('pledge_app.urls')),
    path('gg/', include('global_giving.urls')),
    path('fcra/', include('fcra_app.urls')),
    path('guidestar/', include('guidestar_app.urls')),
    path('irs/', include('irs_app.urls')),
    path('charity/', include('c_navigator.urls')),
    path('gg_india/', include('global_giving_india.urls')),
]

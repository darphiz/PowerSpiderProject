from . views import GGIndiaView
from django.urls import path

urlpatterns = [
    path('', GGIndiaView.as_view(), name='gg_india'),
]
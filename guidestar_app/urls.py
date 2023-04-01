from django.urls import path
from . import views

urlpatterns = [
    path('', views.GuideStarView.as_view(), name='guidestar'),
    
]
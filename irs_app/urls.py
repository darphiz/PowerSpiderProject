from django.urls import path
from . import views

urlpatterns = [
    path('', views.IrsView.as_view() , name='index'),
]
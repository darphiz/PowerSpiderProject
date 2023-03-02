from .views import CharityView
from django.urls import path

urlpatterns = [
    path("", CharityView.as_view(), name="charity"),
]

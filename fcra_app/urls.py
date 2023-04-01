from .views import FCRAView 
from django.urls import path

urlpatterns = [
    path(
        "", FCRAView.as_view(), name="fcra"
    )
]
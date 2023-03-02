from django.urls import path
from .views import GGView

urlpatterns = [
    path('', GGView.as_view(), name="gg"),
]
from . import views
from django.urls import path

urlpatterns = [
    path("", views.LocationView.as_view(), name="location"),
]
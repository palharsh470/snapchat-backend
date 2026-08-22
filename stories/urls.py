from . import views
from django.urls import path

urlpatterns = [
    path("", views.StoriesView.as_view(), name="stories"),
]

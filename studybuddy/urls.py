from django.urls import path

from . import views

# app_name = "studybuddy"
urlpatterns = [
    path("", views.index, name="index"),
    path("join", views.join, name="join"),
    path("join-success", views.joinSuccess, name="join-success"),
    path("optout", views.optout, name="optout"),
    # path("re-pair", views.rePair, name="re-pair"),
]

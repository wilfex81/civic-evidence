from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("project/<slug:slug>/", views.project_detail, name="project_detail"),
    path(
        "project/<slug:slug>/submit/",
        views.submit_observation,
        name="submit_observation",
    ),
]

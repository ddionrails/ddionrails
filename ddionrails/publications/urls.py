# -*- coding: utf-8 -*-

""" URLConf for ddionrails.publications app """

from django.urls import path

from . import views

app_name = "publications"

urlpatterns = [
    path("", views.study_publication_list, name="study_publication_list"),
    path(
        "<slug:publication_name>",
        views.PublicationDetailView.as_view(),
        name="publication_detail",
    ),
]

# -*- coding: utf-8 -*-

""" URLConf for ddionrails.publications app """

from django.urls import path

from .views import PublicationDetailView, study_publication_list

app_name = "publications"

urlpatterns = [
    path("", study_publication_list, name="study_publication_list"),
    path("<slug:publication_name>", PublicationDetailView.as_view(), name="publication"),
]

# -*- coding: utf-8 -*-

""" URLConf for ddionrails.concepts app """

from django.urls import path

from .views import ConceptDetailView, concept_list

app_name = "concepts"

urlpatterns = [
    path("", concept_list, name="concept_list"),
    path("<uuid:id>", ConceptDetailView.as_view(), name="concept_detail"),
    path("<slug:concept_name>", ConceptDetailView.as_view(), name="concept_detail_name"),
]

# -*- coding: utf-8 -*-

""" URLConf for ddionrails.concepts app """

from django.urls import path

from .views import ConceptDetailView, ConceptListView

app_name = "concepts"

urlpatterns = [
    path("", ConceptListView.as_view(), name="concept_list"),
    path("<int:pk>", ConceptDetailView.as_view(), name="concept_detail"),
    path("<slug:concept_name>", ConceptDetailView.as_view(), name="concept_detail_name"),
]

# -*- coding: utf-8 -*-

""" URLConf for ddionrails.concepts app """

from django.urls import path

from .views import ConceptDetail, ConceptList

app_name = "concepts"

urlpatterns = [
    path("", ConceptList.as_view(), name="concept_list"),
    path("<int:pk>", ConceptDetail.as_view(), name="concept_detail"),
    path("<slug:concept_name>", ConceptDetail.as_view(), name="concept_detail_name"),
]

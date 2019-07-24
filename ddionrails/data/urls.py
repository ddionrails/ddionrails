# -*- coding: utf-8 -*-

""" URLConf for ddionrails.data app """

from django.urls import path

from . import views

app_name = "data"

urlpatterns = [
    path("<slug:dataset_name>", views.DatasetDetailView.as_view(), name="dataset_detail"),
    path(
        "<slug:dataset_name>/<slug:variable_name>",
        views.VariableDetailView.as_view(),
        name="variable_detail",
    ),
    path(
        "<slug:dataset_name>/<slug:variable_name>.json",
        views.variable_json,
        name="variable_json",
    ),
]

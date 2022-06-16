# -*- coding: utf-8 -*-

""" URLConf for ddionrails.data app """

from urllib.parse import quote, unquote

from django.urls import path, register_converter

from . import views

app_name = "data"


class DatasetConverter:
    """Get study object from url component."""

    regex = r".*"

    @staticmethod
    def to_python(value):
        """Get object"""
        return unquote(value)

    @staticmethod
    def to_url(value):
        """Return string unchanged"""
        return quote(value)


register_converter(DatasetConverter, "dataset")

urlpatterns = [
    path(
        "",
        views.AllStudyDatasetsView.as_view(),
        name="all_study_datasets",
    ),
    path(
        "<dataset:dataset_name>/",
        views.DatasetDetailView.as_view(),
        name="dataset_detail",
    ),
    path(
        "<dataset:dataset_name>/<slug:variable_name>",
        views.VariableDetailView.as_view(),
        name="variable_detail",
    ),
]

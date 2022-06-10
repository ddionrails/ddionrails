# -*- coding: utf-8 -*-
# pylint: disable=missing-function-docstring,missing-class-docstring

""" URLConf for ddionrails.data app """

from django.urls import path, register_converter
from django.views.generic.base import TemplateView

from . import views

app_name = "statistics"


class TypeConverter:
    regex = "((categorical)|(numerical))"

    @staticmethod
    def to_python(value: str) -> str:
        return value

    @staticmethod
    def to_url(value: str) -> str:
        return value


register_converter(TypeConverter, "type")

urlpatterns = [
    path("", views.StatisticsNavView.as_view(), name="statistics"),
    path(
        "feedback/",
        TemplateView.as_view(template_name="statistics/feedback.html"),
        name="statistics_feedback",
    ),
    path("<type:plot_type>/", views.statistics_detail_view, name="statistics_detail"),
]

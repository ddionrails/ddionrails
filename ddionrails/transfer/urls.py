# -*- coding: utf-8 -*-
# pylint: disable=missing-function-docstring,missing-class-docstring

""" URLConf for ddionrails.data app """

from django.urls import path, register_converter

from . import views

app_name = "transfer"


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
    path("", views.TransferView.as_view(), name="transfer"),
    path("<type:plot_type>/", views.transfer_detail_view, name="transfer_detail"),
]

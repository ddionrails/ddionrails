# -*- coding: utf-8 -*-

""" URLConf for ddionrails.data app """

from django.urls import path

from . import views

app_name = "transfer"

urlpatterns = [
    path("", views.TransferView.as_view(), name="transfer"),
    path("categorical/", views.CategoricalView.as_view(), name="categorical"),
    path("numerical/", views.NumericalView.as_view(), name="numerical"),
]

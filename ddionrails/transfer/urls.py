# -*- coding: utf-8 -*-

""" URLConf for ddionrails.data app """

from django.urls import path

from . import views

app_name = "data"

urlpatterns = [path("categorical/", views.CategoricalView.as_view(), name="categorical")]

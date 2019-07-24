# -*- coding: utf-8 -*-

""" URLConf for ddionrails.instruments app """

from django.urls import path

from . import views

app_name = "instruments"

urlpatterns = [
    path("", views.study_instrument_list, name="study_instrument_list"),
    path(
        "<str:instrument_name>",
        views.InstrumentDetailView.as_view(),
        name="instrument_detail",
    ),
    path(
        "<str:instrument_name>/<str:question_name>",
        views.question_detail,
        name="question_detail",
    ),
]

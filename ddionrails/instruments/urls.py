# -*- coding: utf-8 -*-

""" URLConf for ddionrails.instruments app """

from django.urls import path

from .views import InstrumentDetailView, question_detail, study_instrument_list

app_name = "instruments"

urlpatterns = [
    path("", study_instrument_list, name="study_instrument_list"),
    path(
        "<str:instrument_name>", InstrumentDetailView.as_view(), name="instrument_detail"
    ),
    path(
        "<str:instrument_name>/<str:question_name>",
        question_detail,
        name="question_detail",
    ),
]

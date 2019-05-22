# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.instruments app """

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from model_utils.managers import InheritanceQuerySet

from .models import Instrument, Question


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    """ ModelAdmin for instruments.Instrument """

    list_display = (
        "name",
        "label",
        "get_study_name",
        "get_period_name",
        "get_analysis_unit_name",
    )
    list_filter = ("study", "analysis_unit", "period")
    list_per_page = 25
    list_select_related = ("study", "period", "analysis_unit")
    raw_id_fields = ("study", "period", "analysis_unit")
    search_fields = ("name", "label")

    def get_study_name(self, object: Instrument):
        """ Return the name of the related study """
        try:
            return object.study.name
        except AttributeError:
            return None

    def get_period_name(self, object: Instrument):
        """ Return the name of the related period """
        try:
            return object.period.name
        except AttributeError:
            return None

    def get_analysis_unit_name(self, object: Instrument):
        """ Return the name of the related analysis unit """
        try:
            return object.analysis_unit.name
        except AttributeError:
            return None

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"
    get_period_name.admin_order_field = "period"
    get_period_name.short_description = "period"
    get_analysis_unit_name.admin_order_field = "analysis_unit"
    get_analysis_unit_name.short_description = "analysis_unit"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """ ModelAdmin for instruments.Question """

    list_display = ("sort_id", "name", "label", "get_instrument_name", "get_study_name")
    list_filter = ("instrument__study__name", "instrument__name")
    list_per_page = 25
    raw_id_fields = ("instrument",)
    search_fields = ("name", "label")
    list_select_related = ("instrument", "instrument__study")

    def get_queryset(self, request: WSGIRequest) -> InheritanceQuerySet:
        """ Return an ordered queryset of questions """
        queryset = super().get_queryset(request)
        queryset = queryset.order_by("instrument", "sort_id")
        return queryset

    def get_instrument_name(self, object: Question):
        """ Return the name of the related instrument """
        return object.instrument.name

    def get_study_name(self, object: Question):
        """ Return the name of the related study """
        return object.instrument.study.name

    get_instrument_name.admin_order_field = "instrument"
    get_instrument_name.short_description = "instrument"
    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"

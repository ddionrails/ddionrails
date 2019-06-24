# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.instruments app """

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from model_utils.managers import InheritanceQuerySet

from ddionrails.base.mixins import AdminMixin

from .models import ConceptQuestion, Instrument, Question, QuestionImage, QuestionVariable


@admin.register(Instrument)
class InstrumentAdmin(AdminMixin, admin.ModelAdmin):
    """ ModelAdmin for instruments.Instrument """

    list_display = ("name", "label", "study_name", "period_name", "analysis_unit_name")
    list_filter = ("study", "analysis_unit", "period")
    list_per_page = 25
    list_select_related = ("study", "period", "analysis_unit")
    raw_id_fields = ("study", "period", "analysis_unit")
    search_fields = ("name", "label")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"
    AdminMixin.period_name.admin_order_field = "period"
    AdminMixin.period_name.short_description = "period"
    AdminMixin.analysis_unit_name.admin_order_field = "analysis_unit"
    AdminMixin.analysis_unit_name.short_description = "analysis_unit"


@admin.register(Question)
class QuestionAdmin(AdminMixin, admin.ModelAdmin):
    """ ModelAdmin for instruments.Question """

    list_display = (
        "sort_id",
        "name",
        "label",
        "instrument_name",
        "instrument_study_name",
    )
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

    AdminMixin.instrument_name.admin_order_field = "instrument"
    AdminMixin.instrument_name.short_description = "instrument"
    AdminMixin.instrument_study_name.admin_order_field = "study"
    AdminMixin.instrument_study_name.short_description = "study"


@admin.register(ConceptQuestion)
class ConceptQuestionAdmin(admin.ModelAdmin):
    """ ModelAdmin for instruments.ConceptQuestion """

    list_display = ("concept_id", "question_id")
    list_per_page = 25
    list_select_related = ("concept", "question")
    raw_id_fields = ("concept", "question")


@admin.register(QuestionVariable)
class QuestionVariableAdmin(admin.ModelAdmin):
    """ ModelAdmin for instruments.QuestionVariable """

    list_display = ("question_id", "variable_id")
    list_per_page = 25
    list_select_related = ("question", "variable")
    raw_id_fields = ("question", "variable")


@admin.register(QuestionImage)
class QuestionImageAdmin(admin.ModelAdmin):
    """ ModelAdmin for instruments.QuestionImage """

    list_display = ("id", "label", "language")
    list_per_page = 25
    list_select_related = True
    raw_id_fields = ("question",)

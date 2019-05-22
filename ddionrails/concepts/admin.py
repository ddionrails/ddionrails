# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.concepts app """

from django.contrib import admin

from ddionrails.base.mixins import AdminMixin

from .models import AnalysisUnit, Concept, ConceptualDataset, Period, Topic


@admin.register(AnalysisUnit)
class AnalysisUnitAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.AnalysisUnit """

    list_display = ("name", "label", "label_de")
    list_per_page = 25
    search_fields = ("name", "label", "label_de")


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.Concept """

    list_display = ("name", "label", "label_de")
    list_per_page = 25
    raw_id_fields = ("topics",)
    search_fields = ("name", "label", "label_de")


@admin.register(ConceptualDataset)
class ConceptualDatasetAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.ConceptualDataset """

    list_display = ("name", "label", "label_de")
    list_per_page = 25
    search_fields = ("name", "label", "label_de")


@admin.register(Period)
class PeriodAdmin(AdminMixin, admin.ModelAdmin):
    """ ModelAdmin for concepts.Period """

    list_display = ("name", "label", "study_name")
    list_filter = ("study__name",)
    list_per_page = 25
    list_select_related = ("study",)
    raw_id_fields = ("study",)
    search_fields = ("name", "label")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.Topic """

    list_display = ("name", "label", "label_de")
    list_filter = ("study__name",)
    list_per_page = 25
    raw_id_fields = ("study", "parent")
    search_fields = ("name", "label", "label_de")

# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" ModelAdmin definitions for ddionrails.concepts app """

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ddionrails.base.mixins import AdminMixin

from . import models, resources


@admin.register(models.AnalysisUnit)
class AnalysisUnitAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for concepts.AnalysisUnit """

    list_display = ("name", "label", "label_de", "study_name")
    list_filter = ("study__name",)
    list_per_page = 25
    list_select_related = ("study",)
    search_fields = ("name", "label", "label_de")
    resource_class = resources.AnalysisUnitResource

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"


@admin.register(models.Concept)
class ConceptAdmin(ImportExportModelAdmin):
    """ ModelAdmin for concepts.Concept """

    list_display = ("name", "label", "label_de")
    list_per_page = 25
    raw_id_fields = ("topics",)
    search_fields = ("name", "label", "label_de")
    resource_class = resources.ConceptResource


@admin.register(models.ConceptualDataset)
class ConceptualDatasetAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for concepts.ConceptualDataset """

    list_display = ("name", "label", "label_de", "study_name")
    list_filter = ("study__name",)
    list_per_page = 25
    list_select_related = ("study",)
    search_fields = ("name", "label", "label_de")
    resource_class = resources.ConceptualDatasetResource

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"


@admin.register(models.Period)
class PeriodAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for concepts.Period """

    list_display = ("name", "label", "study_name")
    list_filter = ("study__name",)
    list_per_page = 25
    list_select_related = ("study",)
    raw_id_fields = ("study",)
    search_fields = ("name", "label")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"
    resource_class = resources.PeriodResource


@admin.register(models.Topic)
class TopicAdmin(ImportExportModelAdmin):
    """ ModelAdmin for concepts.Topic """

    list_display = ("name", "label", "label_de")
    list_filter = ("study__name",)
    list_per_page = 25
    raw_id_fields = ("study", "parent")
    search_fields = ("name", "label", "label_de")
    resource_class = resources.TopicResource

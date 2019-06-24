# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" ModelAdmin definitions for ddionrails.data app """

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from ddionrails.base.mixins import AdminMixin

from . import models, resources


@admin.register(models.Dataset)
class DatasetAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for data.Dataset """

    list_display = ("name", "label", "study_name", "period_name", "analysis_unit_name")
    list_filter = ("study__name", "analysis_unit__name", "period__name")
    list_per_page = 25
    list_select_related = ("study", "period", "analysis_unit")
    raw_id_fields = ("study", "conceptual_dataset", "period", "analysis_unit")
    search_fields = ("name", "label")
    resource_class = resources.DatasetResource

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"
    AdminMixin.period_name.admin_order_field = "period"
    AdminMixin.period_name.short_description = "period"
    AdminMixin.analysis_unit_name.admin_order_field = "analysis_unit"
    AdminMixin.analysis_unit_name.short_description = "analysis_unit"


@admin.register(models.Variable)
class VariableAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for data.Variable """

    list_display = ("name", "label", "dataset_name", "dataset_study_name")
    list_filter = ("dataset__study__name",)
    list_per_page = 25
    list_select_related = ("dataset", "dataset__study")
    raw_id_fields = ("dataset", "concept", "period")
    search_fields = ("name", "label")
    resource_class = resources.VariableResource

    AdminMixin.dataset_name.admin_order_field = "dataset"
    AdminMixin.dataset_name.short_description = "dataset"
    AdminMixin.dataset_study_name.admin_order_field = "study"
    AdminMixin.dataset_study_name.short_description = "study"


@admin.register(models.Transformation)
class TransformationAdmin(ImportExportModelAdmin):
    """ ModelAdmin for data.Transformation """

    list_display = ("origin_id", "target_id")
    list_per_page = 25
    list_select_related = ("origin", "target")
    raw_id_fields = ("origin", "target")
    resource_class = resources.TransformationResource

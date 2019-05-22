# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.data app """

from django.contrib import admin

from .models import Dataset, Variable


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """ ModelAdmin for data.Dataset """

    list_display = (
        "name",
        "label",
        "get_study_name",
        "get_period_name",
        "get_analysis_unit_name",
    )
    list_filter = ("study__name", "analysis_unit__name", "period__name")
    list_per_page = 25
    list_select_related = ("study", "period", "analysis_unit")
    raw_id_fields = ("study", "conceptual_dataset", "period", "analysis_unit")
    search_fields = ("name", "label")

    def get_study_name(self, object: Dataset):
        """ Return the name of the related study """
        try:
            return object.study.name
        except AttributeError:
            return None

    def get_period_name(self, object: Dataset):
        """ Return the name of the related period """
        try:
            return object.period.name
        except AttributeError:
            return None

    def get_analysis_unit_name(self, object: Dataset):
        """ Return the name of the related analysis_unit """
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


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    """ ModelAdmin for data.Variable """

    list_display = ("name", "label", "get_dataset_name", "get_study_name")
    list_filter = ("dataset__study__name",)
    list_per_page = 25
    list_select_related = ("dataset", "dataset__study")
    raw_id_fields = ("dataset", "concept", "period")
    search_fields = ("name", "label")

    def get_dataset_name(self, object):
        """ Return the name of the related dataset """
        try:
            return object.dataset.name
        except AttributeError:
            return None

    def get_study_name(self, object):
        """ Return the name of the related study """
        try:
            return object.dataset.study.name
        except AttributeError:
            return None

    get_dataset_name.admin_order_field = "dataset"
    get_dataset_name.short_description = "dataset"
    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"

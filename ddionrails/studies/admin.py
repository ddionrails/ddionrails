# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.studies app """

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count, QuerySet

from .models import Study


class StudyInline(admin.TabularInline):
    model = Study
    extra = 0
    fields = ["name", "label", "repo"]


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    """ ModelAdmin for studies.Study """

    list_display = (
        "name",
        "label",
        "dataset_count",
        "instrument_count",
        "basket_count",
        "created",
        "modified",
    )
    list_per_page = 25

    def get_queryset(self, request: WSGIRequest) -> QuerySet:
        """ Annotate the queryset with aggregated counts of related models """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _dataset_count=Count("datasets", distinct=True),
            _instrument_count=Count("instruments", distinct=True),
            _basket_count=Count("baskets", distinct=True),
        )
        return queryset

    @staticmethod
    def dataset_count(obj: Study) -> int:
        """ Return the number of related datasets from the annotated queryset """
        return obj._dataset_count

    @staticmethod
    def instrument_count(obj: Study) -> int:
        """ Return the number of related instruments from the annotated queryset """
        return obj._instrument_count

    @staticmethod
    def basket_count(obj: Study) -> int:
        """ Return the number of related baskets from the annotated queryset """
        return obj._basket_count

    dataset_count.admin_order_field = "_dataset_count"
    dataset_count.short_description = "Datasets"
    instrument_count.admin_order_field = "_instrument_count"
    instrument_count.short_description = "Instruments"
    basket_count.admin_order_field = "_basket_count"
    basket_count.short_description = "Baskets"

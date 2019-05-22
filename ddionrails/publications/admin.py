# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.publications app """

from django.contrib import admin

from ddionrails.base.mixins import AdminMixin

from .models import Attachment, Publication


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """ ModelAdmin for publications.Attachment """

    list_display = (
        "context_study",
        "study",
        "dataset",
        "variable",
        "instrument",
        "question",
    )
    list_filter = ("context_study",)
    list_per_page = 25
    list_select_related = (
        "context_study",
        "study",
        "instrument",
        "instrument__study",
        "dataset",
        "dataset__study",
        "variable",
        "variable__dataset",
        "variable__dataset__study",
    )
    raw_id_fields = ("context_study", "study", "instrument", "dataset", "variable")
    fields = (
        "context_study",
        "url",
        "url_text",
        "study",
        "instrument",
        "dataset",
        "variable",
    )


@admin.register(Publication)
class PublicationAdmin(AdminMixin, admin.ModelAdmin):
    """ ModelAdmin for publications.Publication """

    list_display = ("name", "title", "author", "study_name", "sub_type", "year")
    list_filter = ("study", "year", "sub_type")
    list_per_page = 25
    list_select_related = ("study",)
    raw_id_fields = ("study",)
    search_fields = ("name", "title", "author")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"

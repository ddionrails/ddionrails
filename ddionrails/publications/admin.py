# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.publications app """

from django.contrib import admin

from .models import Attachment, Publication


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.Concept """

    list_display = ("study", "dataset", "variable", "instrument", "question")
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
class PublicationAdmin(admin.ModelAdmin):
    """ ModelAdmin for concepts.Concept """

    list_display = ("name", "title", "author", "get_study_name", "sub_type", "year")
    list_filter = ("study", "year", "sub_type")
    list_per_page = 25
    list_select_related = ("study",)
    raw_id_fields = ("study",)
    search_fields = ("name", "title", "author")

    def get_study_name(self, object: Publication):
        """ Return the name of the related study """
        try:
            return object.study.name
        except AttributeError:
            return None

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"

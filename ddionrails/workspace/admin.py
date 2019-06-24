# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" ModelAdmin definitions for ddionrails.workspace app """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ImportMixin

from ddionrails.base.mixins import AdminMixin

from . import models, resources


@admin.register(models.Basket)
class BasketAdmin(AdminMixin, ImportExportModelAdmin):
    """ ModelAdmin for workspace.Basket
        The BasketAdmin can import and export basket files
    """

    fields = ("name", "label", "description", "user", "study", "created", "modified")
    readonly_fields = ("created", "modified")
    list_display = ("name", "user", "study_name", "created", "modified")
    list_filter = ("study",)
    list_per_page = 25
    resource_class = resources.BasketResource
    raw_id_fields = ("user", "study")
    search_fields = ("name", "label", "description")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"


@admin.register(models.BasketVariable)
class BasketVariableAdmin(AdminMixin, ImportMixin, admin.ModelAdmin):
    """ ModelAdmin for workspace.BasketVariable
        The BasketVariableAdmin can import basket-variable files
    """

    list_display = ("basket", "basket_study_name", "variable_id")
    list_filter = ("basket__study",)
    list_per_page = 25
    list_select_related = ("basket", "variable")
    resource_class = resources.BasketVariableImportResource
    raw_id_fields = ("basket", "variable")

    AdminMixin.basket_study_name.admin_order_field = "study"
    AdminMixin.basket_study_name.short_description = "study"


@admin.register(models.Script)
class ScriptAdmin(AdminMixin, ImportMixin, admin.ModelAdmin):
    """ ModelAdmin for workspace.Script
        The ScriptAdmin can import script files
    """

    list_display = (
        "name",
        "user_name",
        "basket_name",
        "basket_study_name",
        "generator_name",
        "created",
        "modified",
    )
    list_filter = ("basket__study",)
    list_per_page = 25
    list_select_related = ("basket", "basket__user")
    raw_id_fields = ("basket",)
    readonly_fields = ("created", "modified")
    resource_class = resources.ScriptImportResource
    search_fields = ("name", "label", "generator_name")

    AdminMixin.basket_study_name.admin_order_field = "study"
    AdminMixin.basket_study_name.short_description = "study"
    AdminMixin.user_name.admin_order_field = "user"
    AdminMixin.user_name.short_description = "user"
    AdminMixin.basket_name.admin_order_field = "basket"
    AdminMixin.basket_name.short_description = "basket"


class ImportExportUserAdmin(ImportExportMixin, UserAdmin):
    """ The basket admin can import and export user files """

    resource_class = resources.UserResource


admin.site.unregister(User)
admin.site.register(User, ImportExportUserAdmin)

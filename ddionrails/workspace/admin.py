# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.workspace app """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ImportMixin

from .models import Basket, BasketVariable, Script
from .resources import (
    BasketResource,
    BasketVariableImportResource,
    ScriptImportResource,
    UserResource,
)


@admin.register(Basket)
class BasketAdmin(ImportExportModelAdmin):
    """ ModelAdmin for workspace.Basket
        The BasketAdmin can import and export basket files
    """

    fields = ("name", "label", "description", "user", "study", "created", "modified")
    readonly_fields = ("created", "modified")
    list_display = ("name", "user", "get_study_name", "created", "modified")
    list_per_page = 25
    resource_class = BasketResource
    raw_id_fields = ("user", "study")
    search_fields = ("name", "label", "description")

    def get_study_name(self, object: Basket):
        """ Return the name of the related study """
        return object.study.name

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"


@admin.register(BasketVariable)
class BasketVariableAdmin(ImportMixin, admin.ModelAdmin):
    """ ModelAdmin for workspace.BasketVariable
        The BasketVariableAdmin can import basket-variable files
    """

    list_display = ("basket", "variable")
    list_per_page = 25
    list_select_related = ("basket", "variable")
    resource_class = BasketVariableImportResource
    raw_id_fields = ("basket", "variable")


@admin.register(Script)
class ScriptAdmin(ImportMixin, admin.ModelAdmin):
    """ ModelAdmin for workspace.Script
        The ScriptAdmin can import script files
    """

    list_display = (
        "name",
        "get_user_name",
        "get_basket_name",
        "get_study_name",
        "created",
        "modified",
    )
    list_per_page = 25
    list_select_related = ("basket", "basket__user")
    raw_id_fields = ("basket",)
    readonly_fields = ("created", "modified")
    resource_class = ScriptImportResource

    def get_study_name(self, object: Script):
        """ Return the name of the related study """
        return object.basket.study.name

    def get_basket_name(self, object: Script):
        """ Return the name of the related basket """
        return object.basket.name

    def get_user_name(self, object: Script):
        """ Return the name of the related user """
        return object.basket.user.username

    get_study_name.admin_order_field = "study"
    get_study_name.short_description = "study"
    get_user_name.admin_order_field = "user"
    get_user_name.short_description = "user"
    get_basket_name.admin_order_field = "basket"
    get_basket_name.short_description = "basket"


class ImportExportUserAdmin(ImportExportMixin, UserAdmin):
    """ The basket admin can import and export user files """

    resource_class = UserResource


admin.site.unregister(User)
admin.site.register(User, ImportExportUserAdmin)

# -*- coding: utf-8 -*-
""" ModelAdmin definitions for ddionrails.workspace app """

from django.contrib import admin
from django.contrib.auth.models import User

from ddionrails.base.mixins import AdminMixin

from .models import Basket, BasketVariable, Script


@admin.register(Basket)
class BasketAdmin(AdminMixin, admin.ModelAdmin):
    """ModelAdmin for workspace.Basket
    The BasketAdmin can import and export basket files
    """

    fields = ("name", "label", "description", "user", "study", "created", "modified")
    readonly_fields = ("created", "modified")
    list_display = ("name", "user", "study_name", "created", "modified")
    list_filter = ("study",)
    list_per_page = 25
    raw_id_fields = ("user", "study")
    search_fields = ("name", "label", "description")

    AdminMixin.study_name.admin_order_field = "study"
    AdminMixin.study_name.short_description = "study"


@admin.register(BasketVariable)
class BasketVariableAdmin(AdminMixin, admin.ModelAdmin):
    """ModelAdmin for workspace.BasketVariable
    The BasketVariableAdmin can import basket-variable files
    """

    list_display = ("basket", "basket_study_name", "variable_id")
    list_filter = ("basket__study",)
    list_per_page = 25
    list_select_related = ("basket", "variable")
    raw_id_fields = ("basket", "variable")


@admin.register(Script)
class ScriptAdmin(AdminMixin, admin.ModelAdmin):
    """ModelAdmin for workspace.Script
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
    search_fields = ("name", "label", "generator_name")

    AdminMixin.basket_study_name.admin_order_field = "study"
    AdminMixin.basket_study_name.short_description = "study"
    AdminMixin.user_name.admin_order_field = "user"
    AdminMixin.user_name.short_description = "user"
    AdminMixin.basket_name.admin_order_field = "basket"
    AdminMixin.basket_name.short_description = "basket"


admin.site.unregister(User)

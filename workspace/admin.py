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
    """ The basket admin can import and export script files """
    fields = ("name", "label", "description", "security_token", "user", "study")
    list_display = ("name", "user", "study")
    resource_class = BasketResource


@admin.register(BasketVariable)
class BasketVariableAdmin(ImportMixin, admin.ModelAdmin):
    """ The basket variable admin can import script files """
    list_display = ("basket", "variable")
    list_per_page = 10
    resource_class = BasketVariableImportResource


@admin.register(Script)
class ScriptAdmin(ImportMixin, admin.ModelAdmin):
    """ The script admin can import script files """
    list_select_related = ("basket",)
    list_per_page = 10
    resource_class = ScriptImportResource


class ImportExportUserAdmin(ImportExportMixin, UserAdmin):
    """ The basket admin can import and export user files """
    resource_class = UserResource


admin.site.unregister(User)
admin.site.register(User, ImportExportUserAdmin)

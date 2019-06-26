# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

""" Import export resources for ddionrails.workspace app """

from django.contrib.auth.models import User
from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget

from ddionrails.data.models import Variable
from ddionrails.studies.models import Study

from .models import Basket, BasketVariable, Script


class UserResource(resources.ModelResource):
    """ Import export resource for User model """

    class Meta:  # pylint: disable=missing-docstring
        model = User
        exclude = ("id",)
        import_id_fields = ("username", "email")
        fields = ("username", "email", "password", "date_joined")
        export_order = ("date_joined", "username", "email", "password")


class BasketResource(resources.ModelResource):
    """ Import export resource for Basket model """

    study = Field(attribute="study", widget=ForeignKeyWidget(Study, field="name"))
    user = Field(attribute="user", widget=ForeignKeyWidget(User, field="username"))

    class Meta:  # pylint: disable=missing-docstring
        model = Basket
        import_id_fields = ("user", "name", "study")
        fields = ("name", "label", "description", "user", "study", "created", "modified")
        export_order = (
            "name",
            "label",
            "description",
            "user",
            "study",
            "created",
            "modified",
        )

    def get_queryset(self):
        return (
            self._meta.model.objects.all()
            .select_related("user", "study")
            .only(
                "name",
                "label",
                "description",
                "user__username",
                "study__name",
                "created",
                "modified",
            )
        )


class VariableWidgket(ForeignKeyWidget):
    """
    Find variable by
        - study name
        - dataset name
        - variable name
    """

    def clean(self, value, row=None, *args, **kwargs):
        params = {}
        params["name"] = row["variable"]
        params["dataset__name"] = row["dataset"]
        params["dataset__study__name"] = row["study"]
        return self.model.objects.get(**params)


class BasketWidget(ForeignKeyWidget):
    """ Widget to select basket by name and username """

    def clean(self, value, row=None, *args, **kwargs):
        params = {}
        params["name"] = row["basket"]
        params["user__username"] = row["user"]
        return self.model.objects.get(**params)


class BasketVariableExportResource(resources.ModelResource):
    """ Export resource for basket variable model """

    basket = Field(attribute="basket__name")
    user = Field(attribute="basket__user__username")
    email = Field(attribute="basket__user__email")
    study = Field(attribute="variable__dataset__study__name")
    dataset = Field(attribute="variable__dataset__name")
    variable = Field(attribute="variable__name")

    class Meta:  # pylint: disable=missing-docstring
        model = BasketVariable
        exclude = ("id",)
        export_order = ("basket", "user", "email", "study", "dataset", "variable")

    def get_queryset(self):
        return (
            self._meta.model.objects.all()
            .select_related("basket", "variable")
            .only(
                "basket__name",
                "basket__user__username",
                "variable__name",
                "variable__dataset__name",
                "variable__dataset__study__name",
            )
        )


class BasketVariableImportResource(resources.ModelResource):
    """ Import resource for basket variable model """

    basket = Field(attribute="basket", widget=BasketWidget(Basket, "name"))
    variable = Field(attribute="variable", widget=VariableWidgket(Variable, "name"))

    class Meta:
        model = BasketVariable
        import_id_fields = ("basket", "variable")
        fields = ("basket", "variable")


class ScriptExportResource(resources.ModelResource):
    """ Export resource for script model """

    user = Field(attribute="basket__user__username")
    basket = Field(attribute="basket__name")
    study = Field(attribute="basket__study__name")

    class Meta:
        model = Script
        exclude = ("id",)


class ScriptImportResource(resources.ModelResource):
    """ Import resource for script model """

    basket = Field(attribute="basket", widget=BasketWidget(Basket, "name"))
    user = Field(attribute="basket__user", widget=ForeignKeyWidget(User, "username"))
    study = Field(attribute="basket__study", widget=ForeignKeyWidget(Study, "name"))

    class Meta:
        model = Script
        import_id_fields = (
            "user",
            "basket",
            "name",
            "study",
            "generator_name",
            "settings",
        )
        exclude = ("id", "user", "study")


def determine_model_and_resource(entity: str, method: str) -> tuple:
    """ Determine which model and resource to use """
    if entity == "users":
        return User, UserResource
    if entity == "baskets":
        return Basket, BasketResource
    if entity == "scripts":
        if method == "backup":
            return Script, ScriptExportResource
        if method == "restore":
            return Script, ScriptImportResource
    if entity == "basket_variables":
        if method == "backup":
            return BasketVariable, BasketVariableExportResource
        if method == "restore":
            return BasketVariable, BasketVariableImportResource

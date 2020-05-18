# -*- coding: utf-8 -*-

""" Mixins for ddionrails.base app """

import pathlib
from typing import Dict

from django import forms
from django.conf import settings

from config.helpers import render_markdown


class ModelMixin:
    """
    Default mixins for all classes in DDI on Rails.

    Requires two definition in the ``DOR`` class:

    * io_fields: Fields that are used for the default form and in the default dict.
    * id_fields: Fields that are used for the get_or_create default method.

    Example:

    ::

        from django.db import models
        from ddionrails.mixins import ModelMixin

        class Test(models.Model, ModelMixin):

            name = models.CharField(max_length=255, unique=True)

            class DOR:
                id_fields = ["name"]
                io_fields = ["name"]

    The default value for DOR is:

    ::

        class DOR:
            id_fields = ["name"]
            io_fields = ["name", "label", "description"]

    The ``id_fields`` are also use to construct a default string identifier.
    It is therefore recommended, to order them from the most general to the
    most specific one.

    """

    # Lets views alter the language to be returned
    language = "en"

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["name"]
        io_fields = ["name", "label", "description"]

    @classmethod
    def get(cls, parameters: Dict):
        """
        Default for the get_or_create based on a dict.

        The method uses only relevant identifiers based on ``DOR.id_fields``.
        """
        try:
            definition = {key: parameters[key] for key in cls.DOR.id_fields}
            result = cls.objects.get(**definition)
        except cls.DoesNotExist:
            result = None
        return result

    @classmethod
    def default_form(cls):
        """
        Creates a default form for all attributes defined in ``DOR.io_fields``.
        """

        class DefaultForm(forms.ModelForm):
            class Meta:
                model = cls
                fields = cls.DOR.io_fields

        return DefaultForm

    def to_dict(self) -> Dict:
        """
        Uses the ``DOR.io_fields`` attribute to generate a default
        dict object for the current instance.
        """
        dictionary = dict()
        for field in self.DOR.io_fields:
            value = getattr(self, field)
            try:
                dictionary[field] = value.pk
            except AttributeError:
                dictionary[field] = value
        return dictionary

    def set_language(self, language: str = "en") -> None:
        """ Set the current language of the data object. """

        if language in ("en", "de"):
            self.language = language

    def title(self) -> str:
        """ Returns a title representation using the "label" or "label_de" field,
            with "name" field as fallback
        """
        name = getattr(self, "name", "")
        label = getattr(self, "label", "")
        if self.language == "de":
            label = getattr(self, "label_de", "")
        if label:
            return str(label)
        return str(name)

    def html_description(self):
        """
        Uses the ddionrails Markdown parser (ddionrails.helpers) to render
        the description into HTML.
        """
        try:
            html = render_markdown(self.description)
        except AttributeError:
            html = ""
        return html

    def __str__(self):
        """ Returns a string reprensentation of the instance, using DOR.id_fields """
        result = []
        for field in self.DOR.id_fields:
            value = getattr(self, field)
            try:
                result.append(value.string_id())
            except AttributeError:
                result.append(str(value))
        return "/".join(result)


class ImportPathMixin:  # pylint: disable=R0903
    """ A mixin for models to return an import_path based on their name attribute """

    def import_path(self) -> pathlib.Path:
        """ Returns the instance's import path """
        return settings.IMPORT_REPO_PATH.joinpath(
            self.name, settings.IMPORT_SUB_DIRECTORY
        )


class AdminMixin:
    """ A mixin for ModelAdmins to query related models via methods """

    @staticmethod
    def study_name(obj):
        """ Return the name of the related study """
        try:
            return obj.study.name
        except AttributeError:
            return None

    @staticmethod
    def period_name(obj):
        """ Return the name of the related period """
        try:
            return obj.period.name
        except AttributeError:
            return None

    @staticmethod
    def analysis_unit_name(obj):
        """ Return the name of the related analysis_unit """
        try:
            return obj.analysis_unit.name
        except AttributeError:
            return None

    @staticmethod
    def dataset_name(obj):
        """ Return the name of the related dataset """
        try:
            return obj.dataset.name
        except AttributeError:
            return None

    @staticmethod
    def dataset_study_name(obj):
        """ Return the name of the related dataset.study """
        try:
            return obj.dataset.study.name
        except AttributeError:
            return None

    @staticmethod
    def instrument_name(obj):
        """ Return the name of the related instrument """
        try:
            return obj.instrument.name
        except AttributeError:
            return None

    @staticmethod
    def instrument_study_name(obj):
        """ Return the name of the related instrument.study """
        try:
            return obj.instrument.study.name
        except AttributeError:
            return None

    @staticmethod
    def basket_name(obj):
        """ Return the name of the related basket """
        try:
            return obj.basket.name
        except AttributeError:
            return None

    @staticmethod
    def basket_study_name(obj):
        """ Return the name of the related basket.study """
        try:
            return obj.basket.study.name
        except AttributeError:
            return None

    @staticmethod
    def user_name(obj):
        """ Return the name of the related basket.user """
        try:
            return obj.basket.user.username
        except AttributeError:
            return None

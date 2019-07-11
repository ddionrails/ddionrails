# -*- coding: utf-8 -*-

""" Search document definitions for ddionrails.data app """

from django.conf import settings
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl.registries import registry

from .models import Variable


@registry.register_document
class VariableDocument(Document):
    """ Search document data.Variable """

    # attributes
    dataset = fields.TextField()

    # facets
    analysis_unit = fields.KeywordField()
    conceptual_dataset = fields.KeywordField()
    period = fields.KeywordField()
    study = fields.KeywordField()

    @staticmethod
    def prepare_dataset(variable: Variable) -> str:
        """ Return the related dataset's name """
        return variable.dataset.name

    @staticmethod
    def prepare_study(variable: Variable) -> str:
        """ Return the related study's title """
        return variable.dataset.study.title()

    @staticmethod
    def prepare_analysis_unit(variable: Variable) -> str:
        """ Return the related analysis_unit's or "None" """
        try:
            return variable.dataset.analysis_unit.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_conceptual_dataset(variable: Variable) -> str:
        """ Return the related conceptual_dataset' title or "None" """
        try:
            return variable.dataset.conceptual_dataset.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_period(variable: Variable) -> str:
        """ Return the related period's title or "None" """
        try:
            return variable.dataset.period.title()
        except AttributeError:
            return None

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        doc_type = "variable"

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}variables"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Variable
        fields = (
            "name",
            "label",
            "label_de",
            "description",
            "description_de",
            "description_long",
        )

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type,
        with select related
        dataset, analysis_unit, conceptual_dataset, period and study.
        """
        return (
            super()
            .get_queryset()
            .select_related(
                "dataset",
                "dataset__analysis_unit",
                "dataset__conceptual_dataset",
                "dataset__period",
                "dataset__study",
            )
        )

# -*- coding: utf-8 -*-

""" Search documents for indexing models from ddionrails.data app into Elasticsearch


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from typing import Dict, List, Optional

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Variable


@registry.register_document
class VariableDocument(Document):
    """ Search document data.Variable """

    # doc_type was removed in Elasticsearch 7
    type = fields.KeywordField()

    @staticmethod
    def prepare_type(variable: Variable) -> str:
        return "variable"

    # attributes
    name = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_long = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")
    categories = fields.ObjectField(
        properties={
            "labels": fields.ListField(fields.TextField(analyzer="english")),
            "labels_de": fields.ListField(fields.TextField(analyzer="german")),
        }
    )

    # relations as attributes
    concept = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(analyzer="english"),
            "label_de": fields.TextField(analyzer="german"),
        }
    )
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
    def prepare_analysis_unit(variable: Variable) -> Optional[str]:
        """ Return the related analysis_unit's or None """
        try:
            return variable.dataset.analysis_unit.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_conceptual_dataset(variable: Variable) -> Optional[str]:
        """ Return the related conceptual_dataset' title or None """
        try:
            return variable.dataset.conceptual_dataset.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_period(variable: Variable) -> Optional[str]:
        """ Return the related period's title or None """
        try:
            return variable.dataset.period.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_categories(variable: Variable) -> Dict[str, List[str]]:
        """ Return the variable's categories, only labels and labels_de """
        return {key: variable.categories.get(key) for key in ("labels", "labels_de")}

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}variables"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Variable

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related
        dataset, analysis_unit, conceptual_dataset, period and study.
        """
        return (
            super()
            .get_queryset()
            .select_related(
                "concept",
                "dataset",
                "dataset__analysis_unit",
                "dataset__conceptual_dataset",
                "dataset__period",
                "dataset__study",
            )
        )

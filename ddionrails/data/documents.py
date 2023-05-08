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

import re
from typing import Dict, List, Optional

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from ddionrails.base.generic_documents import GenericDataDocument
from ddionrails.studies.models import Study

from .models import Variable

n_gram_analyzer = analyzer(
    "ngram", tokenizer="ngram", min_gram=3, max_gram=7, filter=["lowercase"]
)


@registry.register_document
class VariableDocument(GenericDataDocument):
    """Search document data.Variable"""

    name = fields.TextField(analyzer=n_gram_analyzer)

    dataset = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(),
            "label_de": fields.TextField(),
        }
    )
    categories = fields.ObjectField(
        properties={
            "labels": fields.ListField(fields.TextField(analyzer="english")),
            "labels_de": fields.ListField(fields.TextField(analyzer="german")),
        }
    )
    conceptual_dataset = fields.KeywordField()

    @staticmethod
    def _get_study(model_object: Variable) -> Study:
        study: Study = model_object.dataset.study
        return study

    def prepare_analysis_unit(self, variable: Variable) -> Optional[str]:
        """Return the related analysis_unit's or None"""
        return self._handle_missing_content(variable.dataset.analysis_unit)

    @staticmethod
    def prepare_categories(variable: Variable) -> Dict[str, List[str]]:
        """Return the variable's categories, only labels and labels_de"""
        output = {}
        for key in ("labels", "labels_de"):
            labels = variable.categories.get(key)
            if labels:
                output[key] = list(
                    filter(
                        lambda label: not re.match(r"\[-\d+\].*", label),
                        labels,
                    )
                )
        return output

    def prepare_conceptual_dataset(self, variable: Variable) -> Optional[str]:
        """Return the related conceptual_dataset' title or None"""
        return self._handle_missing_content(variable.dataset.conceptual_dataset)

    def prepare_period(self, variable: Variable) -> Optional[str]:
        """Return the related period's title or None"""
        return self._handle_missing_content(variable.dataset.period)

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

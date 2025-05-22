# -*- coding: utf-8 -*-
"""Search documents for indexing models from ddionrails.data app into Elasticsearch


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
from itertools import zip_longest
from typing import Dict, List

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.base.generic_documents import (
    GenericDataDocument,
    prepare_model_name_and_labels,
)
from ddionrails.studies.models import Study

from .models import Variable


@registry.register_document
class VariableDocument(GenericDataDocument):
    """Search document data.Variable"""

    name = fields.KeywordField()

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
    conceptual_dataset = fields.ObjectField(
        properties={
            "label": fields.KeywordField(),
            "label_de": fields.KeywordField(),
        }
    )

    @staticmethod
    def _get_study(model_object: Variable) -> Study:
        """Implementation of method from GenericDocument 'interface'"""
        study: Study = model_object.dataset.study
        return study

    @staticmethod
    def prepare_dataset(  # pylint: disable=missing-docstring
        variable: Variable,
    ) -> Dict[str, str]:
        return prepare_model_name_and_labels(variable.dataset)

    def prepare_analysis_unit(self, variable: Variable) -> dict[str, str]:
        """Return the related analysis_unit's or None"""
        return self._handle_missing_dict_content(variable.dataset.analysis_unit)

    @staticmethod
    def prepare_categories(variable: Variable) -> Dict[str, List[str]]:
        """Return the variable's categories, only labels and labels_de"""
        output = {"labels": [], "labels_de": []}
        categories = variable.categories
        if not categories:
            return output
        for value, label, label_de in zip_longest(
            categories.get("values", []),
            categories.get("labels", []),
            categories.get("labels_de", []),
        ):
            if value == ".":
                continue
            if isinstance(value, str) and not value.isnumeric():
                continue
            if value is not None and int(value) < 0:
                continue
            cleaned_label = ""
            cleaned_label_de = ""
            if label:
                cleaned_label = re.sub(r"\[.+?\]\s{0,1}", "", label)
            if label_de:
                cleaned_label_de = re.sub(r"\[.+?\]\s{0,1}", "", label_de)
            output["labels"].append(cleaned_label)
            output["labels_de"].append(cleaned_label_de)

        return output

    def prepare_conceptual_dataset(self, variable: Variable) -> dict[str, str]:
        """Return the related conceptual_dataset' title or None"""
        return self._handle_missing_dict_content(variable.dataset.conceptual_dataset)

    def prepare_period(self, variable: Variable) -> dict[str, str]:
        """Return the related period's title or None"""
        return self._handle_missing_dict_content(variable.dataset.period)

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}variables"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Variable

    def get_queryset(self) -> QuerySet:
        """Return the queryset that should be indexed by this doc type"""
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

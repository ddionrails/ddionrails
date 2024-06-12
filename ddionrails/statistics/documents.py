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

import statistics
from dataclasses import field
from typing import Dict, List, Optional

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.data.models.variable import Variable


@registry.register_document
class VariableStatisticDocument(Document):
    """Search document data.Variable"""

    id = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")

    # relations as attributes
    concept = fields.ObjectField(
        properties={
            "label": fields.TextField(analyzer="english"),
            "label_de": fields.TextField(analyzer="german"),
        }
    )

    # facets
    analysis_unit = fields.KeywordField()
    period = fields.KeywordField()
    study = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(),
        }
    )
    statistics_type = fields.TextField()

    def prepare_study(self, variable):
        return {
            "name": variable.dataset.study.name,
            "label": variable.dataset.study.label,
        }

    def prepare_analysis_unit(self, variable: Variable) -> Optional[str]:
        """Return the related analysis_unit's or None"""
        return self._handle_missing_content(variable.dataset.analysis_unit)

    def prepare_period(self, variable: Variable) -> Optional[str]:
        """Return the related period's title or None"""
        return self._handle_missing_content(variable.dataset.period)

    @staticmethod
    def _handle_missing_content(content: str) -> str:
        if content is None:
            return "Not Categorized"
        if str(content.title()).lower() in ["none", "unspecified"]:
            return "Not Categorized"
        return content.title()

    def get_queryset(self) -> QuerySet[Variable]:
        """Only index variables with statistics data."""
        return Variable.objects.filter(statistics_flag=True).select_related(
            "concept",
            "dataset",
            "dataset__analysis_unit",
            "dataset__period",
            "dataset__study",
        )

    @staticmethod
    def prepare_categories(variable: Variable) -> Dict[str, List[str]]:
        """Return the variable's categories, only labels and labels_de"""
        return {key: variable.categories.get(key) for key in ("labels", "labels_de")}

    # pylint: disable=all
    class Index:
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}statistics"

    class Django:
        model = Variable
        queryset_pagination = 5000  # TODO: Find out if this is the best fix

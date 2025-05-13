# -*- coding: utf-8 -*-

""" Documents for indexing Instrument model into Elasticsearch


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from typing import Dict

from django.conf import settings
from django.db.models.query import QuerySet
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.base.generic_documents import (
    GenericDataDocument,
    prepare_model_name_and_labels,
)
from ddionrails.instruments.models.question import Question
from ddionrails.studies.models import Study


@registry.register_document
class QuestionDocument(GenericDataDocument):
    """Search document instruments.Question"""

    name = fields.TextField()

    label = fields.TextField()

    instrument = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(),
            "label_de": fields.TextField(),
        }
    )
    question_items = fields.ObjectField(
        properties={
            "en": fields.ListField(fields.TextField(analyzer="english")),
            "de": fields.ListField(fields.TextField(analyzer="german")),
        }
    )

    @staticmethod
    def _get_study(model_object: Question) -> Study:
        study: Study = getattr(model_object.instrument, "study")
        return study

    # lookup methods
    def prepare_analysis_unit(self, question: Question) -> dict[str, str]:
        """Return the related analysis_unit's or None"""
        return self._handle_missing_dict_content(question.instrument.analysis_unit)

    def prepare_instrument(self, question: Question) -> dict[str, str]:
        """Return the related analysis_unit's or None"""
        return prepare_model_name_and_labels(question.instrument)

    def prepare_period(self, question: Question) -> dict[str, str]:
        """Return the related period's title or None"""
        return self._handle_missing_dict_content(question.instrument.period)

    @staticmethod
    def prepare_items(question: Question) -> Dict:
        """Return the question's items, containing text, text_de and answers"""
        items = {"en": [], "de": []}
        for item in question.items:
            text = item.get("text")
            text_de = item.get("text_de")
            if text:
                items["en"].append(text)
            if text_de:
                items["de"].append(text_de)
            answers = item.get("answers", [])
            for answer in answers:
                label = answer.get("label")
                label_de = answer.get("label_de")
                if label:
                    items["en"].append(label)
                if label_de:
                    items["de"].append(label_de)
        return items

    class Index:  # pylint: disable=too-few-public-methods missing-class-docstring
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}questions"

    class Django:  # pylint: disable=too-few-public-methods missing-class-docstring
        model = Question

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related instrument, study, period.
        """
        return (
            super()
            .get_queryset()
            .select_related(
                "instrument",
                "instrument__analysis_unit",
                "instrument__period",
                "instrument__study",
            )
        )

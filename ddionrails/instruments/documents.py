# -*- coding: utf-8 -*-

""" Search documents for indexing models from ddionrails.instruments app into Elasticsearch


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from typing import Dict, Optional

from django.conf import settings
from django.db.models.query import QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Question


@registry.register_document
class QuestionDocument(Document):
    """ Search document instruments.Question """

    # attributes
    name = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")
    items = fields.ObjectField(
        properties={
            "en": fields.ListField(fields.TextField(analyzer="english")),
            "de": fields.ListField(fields.TextField(analyzer="german")),
        }
    )

    # relations
    analysis_unit = fields.KeywordField()
    instrument = fields.TextField(fields={"raw": fields.KeywordField()})
    period = fields.KeywordField()
    study = fields.KeywordField()

    # lookup methods
    @staticmethod
    def prepare_analysis_unit(question: Question) -> Optional[str]:
        """ Return the related analysis_unit's or None """
        try:
            return question.instrument.analysis_unit.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_instrument(question: Question) -> str:
        """ Return the related instrument's title """
        return question.instrument.title()

    @staticmethod
    def prepare_period(question: Question) -> Optional[str]:
        """ Return the related period's title or None """
        try:
            return question.instrument.period.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_study(question: Question) -> str:
        """ Return the related study's title """
        return question.instrument.study.title()

    @staticmethod
    def prepare_items(question: Question) -> Dict:
        """ Return the question's items, containing text, text_de and answers """
        items = {"en": [], "de": []}
        for item in question.items:
            text = item.get("text")
            text_de = item.get("text_de")
            if text:
                items["en"].append(text)
            if text_de:
                items["de"].append(text_de)
            answers = item.get("answers", list())
            for answer in answers:
                label = answer.get("label")
                label_de = answer.get("label_de")
                if label:
                    items["en"].append(label)
                if label_de:
                    items["de"].append(label_de)
        return items

    class Meta:  # pylint: disable=too-few-public-methods
        doc_type = "question"

    class Index:  # pylint: disable=too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}questions"

    class Django:  # pylint: disable=too-few-public-methods
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
            .only(
                "items",
                "name",
                "label",
                "label_de",
                "instrument__name",
                "instrument__label",
                "instrument__analysis_unit__name",
                "instrument__analysis_unit__label",
                "instrument__period__name",
                "instrument__period__label",
                "instrument__study__name",
                "instrument__study__label",
            )
        )

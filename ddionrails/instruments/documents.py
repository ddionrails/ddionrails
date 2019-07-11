# -*- coding: utf-8 -*-

""" Search document definitions for ddionrails.instruments app """

from django.conf import settings
from django.db.models.query import QuerySet
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from .models import Question

my_analyzer = analyzer(
    "my_analyzer",
    # tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
    filter=["lowercase"],
)


@registry.register_document
class QuestionDocument(Document):
    """ Search document instruments.Question """

    # attributes
    items = fields.ObjectField(properties={"text": fields.TextField()})
    label = fields.TextField(analyzer="english")

    # relations
    analysis_unit = fields.KeywordField()
    instrument = fields.TextField(fields={"raw": fields.KeywordField()})
    period = fields.KeywordField()
    study = fields.TextField(fields={"raw": fields.KeywordField()})

    # lookup methods
    @staticmethod
    def prepare_analysis_unit(question: Question) -> str:
        """ Return the related analysis_unit's or "None" """
        try:
            return question.instrument.analysis_unit.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_instrument(question: Question) -> str:
        """ Return the related instrument's title """
        return question.instrument.title()

    @staticmethod
    def prepare_period(question: Question) -> str:
        """ Return the related period's title or "None" """
        try:
            return question.instrument.period.title()
        except AttributeError:
            return None

    @staticmethod
    def prepare_study(question: Question) -> str:
        """ Return the related study's title """
        return question.instrument.study.title()

    @staticmethod
    def prepare_items(question: Question):
        items = []
        for item in question.items:
            items.append(
                dict(
                    text=item.get("text"),
                    text_de=item.get("text_de"),
                    instruction=item.get("instruction"),
                    instruction_de=item.get("instruction_de"),
                )
            )
        return items

    class Meta:  # pylint: disable=too-few-public-methods
        doc_type = "question"

    class Index:  # pylint: disable=too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}questions"

    class Django:  # pylint: disable=too-few-public-methods
        model = Question
        fields = ("name", "label_de", "description", "description_de")

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

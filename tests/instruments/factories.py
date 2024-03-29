# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.instruments app """

import factory

from ddionrails.instruments.models import (
    ConceptQuestion,
    Instrument,
    Question,
    QuestionItem,
    QuestionVariable,
)
from tests.concepts.factories import AnalysisUnitFactory, ConceptFactory, PeriodFactory
from tests.data.factories import VariableFactory
from tests.studies.factories import StudyFactory


class InstrumentFactory(factory.django.DjangoModelFactory):
    """Instrument factory"""

    analysis_unit = factory.SubFactory(AnalysisUnitFactory, name="some-analysis-unit")
    period = factory.SubFactory(PeriodFactory, name="some-period")
    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Instrument
        django_get_or_create = ("study", "name")


class QuestionFactory(factory.django.DjangoModelFactory):
    """Question factory"""

    instrument = factory.SubFactory(InstrumentFactory, name="some-instrument")

    class Meta:
        model = Question
        django_get_or_create = ("instrument", "name")


class QuestionItemFactory(factory.django.DjangoModelFactory):

    question = factory.SubFactory(QuestionFactory, name="some-question")
    position = 1

    class Meta:
        model = QuestionItem
        django_get_or_create = ("question", "name")


class ConceptQuestionFactory(factory.django.DjangoModelFactory):
    """ConceptQuestion factory"""

    concept = factory.SubFactory(ConceptFactory, name="some-concept")
    question = factory.SubFactory(QuestionFactory, name="some-question", sort_id=1)

    class Meta:
        model = ConceptQuestion


class QuestionVariableFactory(factory.django.DjangoModelFactory):
    """QuestionVariable factory"""

    question = factory.SubFactory(QuestionFactory, name="some-question", sort_id=1)
    variable = factory.SubFactory(VariableFactory, name="some-variable")

    class Meta:
        model = QuestionVariable

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.instruments app """

import factory

from ddionrails.instruments.models import (
    ConceptQuestion,
    Instrument,
    Question,
    QuestionVariable,
)
from tests.concepts.factories import ConceptFactory, PeriodFactory
from tests.data.factories import VariableFactory
from tests.studies.factories import StudyFactory


class InstrumentFactory(factory.django.DjangoModelFactory):
    """Instrument factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")
    period = factory.SubFactory(PeriodFactory, name="some-period")

    class Meta:
        model = Instrument
        django_get_or_create = ("study", "name")


class QuestionFactory(factory.django.DjangoModelFactory):
    """Question factory"""

    instrument = factory.SubFactory(InstrumentFactory, name="some-instrument")

    class Meta:
        model = Question
        django_get_or_create = ("instrument", "name")


class ConceptQuestionFactory(factory.django.DjangoModelFactory):
    """ConceptQuestion factory"""

    concept = factory.SubFactory(ConceptFactory, name="some-concept")
    question = factory.SubFactory(QuestionFactory, name="some-question")

    class Meta:
        model = ConceptQuestion


class QuestionVariableFactory(factory.django.DjangoModelFactory):
    """QuestionVariable factory"""

    question = factory.SubFactory(QuestionFactory, name="some-question")
    variable = factory.SubFactory(VariableFactory, name="some-variable")

    class Meta:
        model = QuestionVariable

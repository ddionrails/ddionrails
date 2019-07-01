# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.data app """

import factory

from ddionrails.data.models import Dataset, Transformation, Variable
from tests.concepts.factories import PeriodFactory
from tests.studies.factories import StudyFactory


class DatasetFactory(factory.django.DjangoModelFactory):
    """Dataset factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")
    period = factory.SubFactory(PeriodFactory, name="some-period")

    class Meta:
        model = Dataset
        django_get_or_create = ("study", "name")


class VariableFactory(factory.django.DjangoModelFactory):
    """Variable factory"""

    dataset = factory.SubFactory(DatasetFactory, name="some-dataset")

    class Meta:
        model = Variable
        django_get_or_create = ("dataset", "name")


class TransformationFactory(factory.django.DjangoModelFactory):
    """Transformation factory"""

    origin = factory.SubFactory(VariableFactory, name="some-origin-variable")
    target = factory.SubFactory(VariableFactory, name="some-target-variable")

    class Meta:
        model = Transformation

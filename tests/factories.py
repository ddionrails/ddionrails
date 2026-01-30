# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods
# type: ignore[override]
"""DjangoModelFactories for user model"""


import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from faker import Faker

from ddionrails.concepts.models import Period
from ddionrails.studies.models import Study

FAKE = Faker()


def german_paragraph(_):
    with factory.Faker.override_default_locale("de_DE"):
        paragraphs = FAKE.paragraphs()
    return paragraphs


def german_label(_):
    with factory.Faker.override_default_locale("de_DE"):
        word = FAKE.word()
    return word


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = "test_user"
    password = factory.PostGenerationMethodCall("set_password", "secret-password")


class StudyFactory(DjangoModelFactory):
    class Meta:
        model = Study

    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(german_label)
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(german_paragraph)


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period


# TODO: Rework this with all general factories
def study_factory(): ...

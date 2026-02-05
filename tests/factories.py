# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods
# type: ignore[override]
"""DjangoModelFactories for user model"""


from typing import TYPE_CHECKING
from uuid import UUID

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker

from ddionrails.concepts.models import Period
from ddionrails.data.models.dataset import Dataset
from ddionrails.data.models.transformation import Transformation
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.instruments.models.question import Question
from ddionrails.instruments.models.question_variable import QuestionVariable
from ddionrails.studies.models import Study

FAKE = Faker()
FAKE_DE = Faker(locale="de_DE")

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = "test_user"
    password = factory.PostGenerationMethodCall("set_password", "secret-password")


class AdminUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: FAKE.user_name())
    email = factory.LazyAttribute(lambda _: FAKE.email())
    is_staff = True
    is_superuser = True
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or FAKE.password(length=9)
        self.set_password(password)
        if create:
            self.save()


class StudyFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Study

    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period


class DatasetFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Dataset

    study = factory.SubFactory(StudyFactory)
    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())


class VariableFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Variable

    dataset = factory.SubFactory(DatasetFactory)
    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())
    statistics = factory.LazyAttribute(
        lambda _: {
            "valid": str(FAKE.random_number()),
            "invalid": str(FAKE.random_number()),
        },
    )
    categories = factory.LazyAttribute(
        lambda _: {
            "frequencies": [FAKE.random_number(), FAKE.random_number()],
            "labels": [
                "[-6] Version of questionnaire with modified filtering",
                "[1] " + FAKE.word(),
            ],
            "labels_de": [
                "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
                "[1] " + FAKE_DE.word(),
            ],
            "values": ["-6", "1"],
            "missings": [True, False],
        }
    )


class TransformationFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        origin: Variable
        target: Variable

    class Meta:
        model = Transformation

    id: UUID
    origin = factory.SubFactory(VariableFactory)
    target = factory.SubFactory(VariableFactory)


class InstrumentFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Instrument

    study = factory.SubFactory(StudyFactory)
    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())


class QuestionFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Question

    instrument = factory.SubFactory(InstrumentFactory)
    name = factory.LazyAttribute(lambda _: FAKE.word())
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    sort_id = factory.Sequence(lambda n: n + 1)


class QuestionVariableFactory(factory.django.DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = QuestionVariable

    question = factory.SubFactory(QuestionFactory, name="some-question", sort_id=1)
    variable = factory.SubFactory(VariableFactory, name="some-variable")

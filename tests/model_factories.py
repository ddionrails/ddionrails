# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods
# type: ignore[override]
"""DjangoModelFactories for user model"""

from collections.abc import Iterable
from random import choice, randint
from typing import TYPE_CHECKING
from uuid import UUID

import factory
from django.contrib.auth import get_user_model
from factory.declarations import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from ddionrails.base.models import News
from ddionrails.concepts.models import (
    AnalysisUnit,
    Concept,
    ConceptualDataset,
    Period,
    Topic,
)
from ddionrails.data.models.dataset import Dataset
from ddionrails.data.models.transformation import Transformation
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.instruments.models.question import Question
from ddionrails.instruments.models.question_item import QuestionItem
from ddionrails.instruments.models.question_variable import QuestionVariable
from ddionrails.publications.models import Attachment, Publication
from ddionrails.studies.models import Study
from ddionrails.workspace.models.basket import Basket

FAKE = Faker()
FAKE_DE = Faker(locale="de_DE")

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"{FAKE.user_name()}_{n}")
    email = factory.LazyAttribute(lambda _: FAKE.email())
    is_staff = False
    is_superuser = False
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or FAKE.password(length=9)
        self.set_password(password)
        if create:
            self.save()


class AdminUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"{FAKE.user_name()}_{n}")
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

    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    class Params:
        depth = 0

    @factory.post_generation
    def parent(self, create, extracted, **kwargs):  # pylint: disable=method-hidden

        if isinstance(extracted, TopicFactory):
            self.parent = extracted
        depth = kwargs.get("depth", 0)
        if depth:
            self.parent = TopicFactory(study=self.study, parent__depth=depth - 1)

        if create:
            self.save()

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class ConceptFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Concept

    class Params:
        study = factory.SubFactory(StudyFactory)
        topics_size = 1

    @factory.post_generation
    def topics(self, create, extracted, **kwargs):  # pylint: disable=method-hidden
        if isinstance(extracted, Iterable):
            for extract in extracted:
                self.topics.add(extract)
            self.save()
            return
        study = kwargs.get("study")
        if create and study is None:
            study = StudyFactory()
        for _ in range(kwargs.get("topics_size", 0)):
            self.topics.add(TopicFactory(study=study))

        if create:
            self.save()

    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class ConceptualDatasetFactory(DjangoModelFactory):

    class Meta:
        model = ConceptualDataset

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())


class AnalysisUnitFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = AnalysisUnit

    study = factory.SubFactory(StudyFactory)

    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())


class DatasetFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Dataset

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())

    analysis_unit = SubFactory(AnalysisUnitFactory)
    period = SubFactory(PeriodFactory)
    conceptual_dataset = SubFactory(ConceptualDatasetFactory)


class VariableFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID
        concept: Concept

    class Meta:
        model = Variable

    @factory.post_generation
    def concept(self, create, extracted, **kwargs):  # pylint: disable=method-hidden
        if extracted:
            self.concept = extracted
            self.save()
            return
        self.concept = ConceptFactory(
            topics__study=self.dataset.study, topics__topics_size=1
        )

        if create:
            self.save()

    dataset = factory.SubFactory(DatasetFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
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


class PublicationFactory(DjangoModelFactory):

    class Meta:
        model = Publication

    name = factory.Sequence(lambda n: f"{n}")
    type = factory.LazyAttribute(lambda _: FAKE.word())
    title = factory.LazyAttribute(lambda _: FAKE.sentence())
    author = factory.LazyAttribute(
        lambda _: ", ".join([FAKE.name() for _ in range(randint(1, 10))])
    )
    year = factory.LazyAttribute(lambda _: FAKE.year())
    abstract = factory.LazyAttribute(lambda _: FAKE.paragraph())
    cite = factory.LazyAttribute(lambda _: FAKE.sentence())
    url = factory.LazyAttribute(lambda _: FAKE.url())
    doi = factory.LazyAttribute(lambda _: FAKE.doi())
    study = factory.SubFactory(StudyFactory)


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
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())


class QuestionItemFactory(DjangoModelFactory):

    class Meta:
        model = QuestionItem

    question = factory.LazyAttribute(lambda _: QuestionFactory())
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    scale = factory.LazyAttribute(lambda _: choice(["txt", "cat", "bin", "int", "chr"]))
    position = 1


class QuestionFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Question

    class Params:
        size = 0

    @factory.post_generation
    def question_items(self, create, extracted, **kwargs):
        if isinstance(extracted, Iterable):
            for extract in extracted:
                self.question_items.add(extract)
            self.save()
            return
        for position in range(kwargs.get("size", 0)):
            self.question_items.add(QuestionItemFactory(question=self, position=position))

        if create:
            self.save()

    instrument = factory.SubFactory(InstrumentFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
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


class BasketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Basket

    study = factory.SubFactory(StudyFactory)
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())

    @factory.post_generation
    def variables(self, create, extracted, **kwargs):
        if isinstance(extracted, Iterable):
            for extract in extracted:
                self.variables.add(extract)
            self.save()
            return
        for _ in range(kwargs.get("basket_size", 0)):
            self.variables.add(Variable(study=self.study))

        if create:
            self.save()


class AttachmentFactory(DjangoModelFactory):

    url = factory.LazyAttribute(lambda _: FAKE.url)
    url_text = factory.LazyAttribute(lambda _: FAKE.sentence())
    context_study = factory.SubFactory(StudyFactory)
    study = factory.SubFactory(StudyFactory)
    dataset = factory.SubFactory(DatasetFactory)
    variable = factory.SubFactory(VariableFactory)
    instrument = factory.SubFactory(InstrumentFactory)
    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Attachment


class NewsFactory(DjangoModelFactory):

    class Meta:
        model = News

    content = factory.LazyAttribute(
        lambda _: "\n".join([f"- {FAKE.sentence()}" for _ in range(3)])
    )
    content_de = factory.LazyAttribute(
        lambda _: "\n".join([f"- {FAKE_DE.sentence()}\n" for _ in range(3)])
    )

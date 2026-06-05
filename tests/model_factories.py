# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,protected-access
# type: ignore[override]
# nosec
"""DjangoModelFactories for user model"""

from collections.abc import Iterable
from random import choice, randint
from typing import TYPE_CHECKING, Any, Generator, Union, cast
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
from ddionrails.instruments.models.answer import Answer
from ddionrails.instruments.models.concept_question import ConceptQuestion
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


def safe_word():
    word = FAKE.word(part_of_speech="noun")
    while word == "none":
        word = FAKE.word(part_of_speech="noun")
    return word


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
    repo = factory.LazyAttribute(lambda _: FAKE.url())


class PeriodFactory(DjangoModelFactory):
    class Meta:
        model = Period

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: safe_word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    def _to_csv(self) -> dict[str, str]:
        return {
            "study": self.study.name,
            "name": self.name,
            "label": self.label,
            "label_de": self.label_de,
            "description": self.description,
            "definition": self.description,
            "description_de": self.description_de,
        }


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    class Params:
        depth = 0

    @factory.post_generation
    def parent(self, create, extracted, **kwargs):  # pylint: disable=method-hidden

        if isinstance(extracted, Topic):
            self.parent = extracted
        depth = kwargs.get("depth", 0)
        if depth:
            self.parent = TopicFactory(study=self.study, parent__depth=depth - 1)

        if create:
            self.save()

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.sentence())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.sentence())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    def _to_csv(self) -> Generator[dict[str, str], None, dict[str, str]]:
        topic = self
        while topic.parent:
            yield {
                "study": topic.study.name,
                "name": topic.name,
                "label": topic.label,
                "label_de": topic.label_de,
                "description": topic.description,
                "definition": topic.description,
                "description_de": topic.description_de,
            }
            topic = topic.parent

        return {
            "study": topic.study.name,
            "name": topic.name,
            "label": topic.label,
            "label_de": topic.label_de,
            "description": topic.description,
            "definition": topic.description,
            "description_de": topic.description_de,
        }


class ConceptFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Concept

    class Params:
        study = factory.SubFactory(StudyFactory)
        size = 1

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
        for _ in range(kwargs.get("size", 0)):
            self.topics.add(TopicFactory(study=study))

        if create:
            self.save()

    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.sentence())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.sentence())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    class _EmptyTopic:
        class _EmptyStudy:
            name = ""

        name = ""
        study = _EmptyStudy()

    def _to_csv(self) -> Generator[dict[str, str], None, dict[str, str]]:
        topics = [self._EmptyTopic()]
        if self.topics.count() > 0:
            topics = self.topics.all()
        for topic in topics:
            return {
                "study": topic.study.name,
                "name": self.name,
                "label": self.label,
                "label_de": self.label_de,
                "description": self.description,
                "definition": self.description,
                "description_de": self.description_de,
                "topic": topic.name,
            }


class ConceptualDatasetFactory(DjangoModelFactory):

    class Meta:
        model = ConceptualDataset

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    def _to_csv(self) -> dict[str, str]:
        return {
            "study": self.study.name,
            "name": self.name,
            "label": self.label,
            "label_de": self.label_de,
            "description": self.description,
            "definition": self.description,
            "description_de": self.description_de,
        }


class AnalysisUnitFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = AnalysisUnit

    study = factory.SubFactory(StudyFactory)

    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: safe_word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    def _to_csv(self) -> dict[str, str]:
        return {
            "study": self.study.name,
            "name": self.name,
            "label": self.label,
            "label_de": self.label_de,
            "description": self.description,
            "definition": self.description,
            "description_de": self.description_de,
        }


class DatasetFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Dataset

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    folder = factory.LazyAttribute(lambda _: FAKE.word())
    primary_key = factory.LazyAttribute(lambda _: "")

    analysis_unit = SubFactory(AnalysisUnitFactory)
    period = SubFactory(PeriodFactory)
    conceptual_dataset = SubFactory(ConceptualDatasetFactory)

    def _to_json(self) -> Generator[dict[str, any], None, None]:
        variables = Variable.objects.filter(dataset=self)

        for variable in variables:
            yield VariableFactory._variable_to_json(variable)

    def _to_csv(self) -> dict[str, str]:
        if self.primary_key == "":
            variable = Variable.objects.filter(dataset=self).first()
            if variable:
                self.primary_key = variable.name

        return {
            "study": self.study.name,
            "name": self.name,
            "label": self.label,
            "label_de": self.label_de,
            "description": self.description,
            "definition": self.description,
            "description_de": self.description_de,
            "analysis_unit": self.analysis_unit.name,
            "conceptual_dataset": self.conceptual_dataset.name,
            "folder": self.folder,
            "primary_key": self.primary_key,
        }


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
        self.concept = ConceptFactory(topics__study=self.dataset.study, topics__size=1)

        if create:
            self.save()

    dataset = factory.SubFactory(DatasetFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.sentence())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.sentence())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())
    scale = factory.LazyAttribute(lambda _: FAKE.word())
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

    def _to_json(self):
        return self._variable_to_json(self)

    @staticmethod
    def _variable_to_json(variable: Union[Variable, "VariableFactory"]):
        return {
            "study": variable.dataset.study.name,
            "dataset": variable.dataset.name,
            "name": variable.name,
            "label": variable.label,
            "label_de": variable.label_de,
            "categories": variable.categories,
            "scale": variable.scale,
            "statistics": variable.statistics,
        }

    def _to_csv(self):
        additional_fields = {
            "description": self.description,
            "description_de": self.description_de,
            "concept": self.concept.name,
        }
        return {**self._variable_to_json(self), **additional_fields}


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
    studies = factory.LazyAttribute(
        lambda _: ", ".join([FAKE.word() for _ in range(randint(1, 10))])
    )

    def _to_csv(self):
        return {
            "study": self.study.name,
            "name": self.name,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "abstract": self.abstract,
            "cite": self.cite,
            "type": self.type,
            "studies": self.studies,
            "url": self.url,
            "doi": self.doi,
        }


class TransformationFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        origin: Variable
        target: Variable

    class Meta:
        model = Transformation

    id: UUID
    origin = factory.SubFactory(VariableFactory)
    target = factory.SubFactory(VariableFactory)

    def _to_csv(self):
        return {
            "origin_study_name": self.origin.dataset.study.name,
            "origin_dataset_name": self.origin.dataset.name,
            "origin_variable_name": self.origin.dataset.name,
            "target_study_name": self.target.dataset.study.name,
            "target_dataset_name": self.target.dataset.name,
            "target_variable_name": self.target.dataset.name,
        }


class InstrumentFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID
        type: dict[str, Any]

    class Meta:
        model = Instrument

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())
    mode = factory.LazyAttribute(lambda _: FAKE.word())
    type = factory.LazyAttribute(
        lambda _: {
            "en": FAKE.sentence(),
            "de": FAKE_DE.sentence(),
            "position": FAKE.random_number(),
        }
    )
    analysis_unit = factory.SubFactory(AnalysisUnitFactory)
    period = factory.SubFactory(PeriodFactory, study=factory.SelfAttribute("..study"))

    def _to_csv(self):
        _type: dict[str, Any] = cast(dict[str, Any], self.type)
        return {
            "study": self.study.name,
            "name": self.name,
            "label": self.label,
            "label_de": self.label_de,
            "description": self.description,
            "description_de": self.description_de,
            "analysis_unit": self.analysis_unit.name,
            "period": self.period.name,
            "mode": self.mode,
            "type": _type["end"],  # pylint: disable=unsubscriptable-object
            "type_de": _type["de"],  # pylint: disable=unsubscriptable-object
            "type_position": _type["position"],  # pylint: disable=unsubscriptable-object
        }

    def _to_json(self):
        instrument_data = self._to_csv()
        for field in ["analysis_unit", "description", "description_de"]:
            del instrument_data[field]
        questions = {}
        for question in Question.objects.filter(dataset=self):
            items = []
            for item in question.items.all():
                items.append(QuestionItemFactory._to_json(item))

            questions[question.name] = {
                "question": question.name,
                "name": question.name,
                "label": question.label,
                "label_de": question.label_de,
                "items": items,
            }
        instrument_data["questions"] = questions


class AnswerFactory(DjangoModelFactory):

    class Meta:
        model = Answer

    value = factory.Sequence(lambda n: n)
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
    position = factory.Sequence(lambda n: n)

    instruction = factory.LazyAttribute(lambda _: FAKE_DE.sentence())
    instruction_de = factory.LazyAttribute(lambda _: FAKE_DE.sentence())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())
    input_filter = factory.LazyAttribute(lambda _: FAKE_DE.password(length=5))
    goto = factory.LazyAttribute(lambda _: FAKE_DE.password(length=5))

    @factory.post_generation
    def answers(self, create, extracted, **kwargs):  # pylint: disable=method-hidden
        if isinstance(extracted, Iterable):
            for extract in extracted:
                self.answers.add(extract)
            self.save()
            return
        if self.scale == "cat":
            numbers = list(range(randint(-9, -1), -1)) + list(range(1, randint(1, 10)))
            for number in numbers:
                self.answers.add(AnswerFactory(value=number))
        if create:
            self.save()

    @staticmethod
    def _to_json(item: QuestionItem):
        output = {
            "item": item.name,
            "text": item.label,
            "text_de": item.label_de,
            "scale": item.scale,
            "sn": item.position,
        }
        answers = []
        for answer in item.answers.all():
            answers.append(
                {
                    "value": answer.value,
                    "label": answer.label,
                    "label_de": answer.label_de,
                }
            )
        if answers:
            output["answers"] = answers
        return output


class QuestionFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Question

    class Params:
        size = 0
        cat_min = 0

    @factory.post_generation
    def question_items(self, create, extracted, **kwargs):
        if isinstance(extracted, Iterable):
            for extract in extracted:
                self.question_items.add(extract)
            self.save()
            return
        cat_min = kwargs.get("cat_min", 0)
        full_size = kwargs.get("size", 0) + cat_min
        for position in range(full_size):
            if cat_min > 0:
                self.question_items.add(
                    QuestionItemFactory(question=self, position=position, scale="cat")
                )
                cat_min = cat_min - 1
                continue
            self.question_items.add(QuestionItemFactory(question=self, position=position))

        if create:
            self.save()

    @factory.post_generation
    def concepts_questions(self, create, extracted, **kwargs):
        if not create:
            return
        if isinstance(extracted, Iterable):
            for concept_question in extracted:
                self.concepts_question.add(concept_question)
            return

        for _ in range(kwargs.get("size", 0)):
            concept = ConceptFactory(topics__study=self.instrument.study)
            self.concepts_questions.add(
                ConceptQuestionFactory(question=self, concept=concept)
            )
        self.save()

    instrument = factory.SubFactory(InstrumentFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.sentence())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.sentence())

    sort_id = factory.Sequence(lambda n: n + 1)

    def _to_csv(self) -> tuple[dict[str, str], dict[str, str]]:
        instrument_name = self.instrument.name
        study_name = self.instrument.study.name
        questions_csv = []
        answers_csv = []

        for item in self.question_items.all().order_by("position"):
            questions_csv.append(
                {
                    "study": study_name,
                    "instrument": instrument_name,
                    "name": self.name,
                    "item": item.name,
                    "text": item.label,
                    "text_de": item.label_de,
                    "instruction": item.instruction,
                    "instruction_de": item.instruction_de,
                    "description": item.description,
                    "description_de": item.description_de,
                    "filter": item.input_filter,
                    "goto": item.goto,
                    "concept": self.concept,
                    "scale": item.scale,
                }
            )
            if item.scale == "cat":
                answer_list = item.id
                for answer in item.answers.all():
                    answers_csv.append(
                        {
                            "study": self.study,
                            "instrument": self.instrument.name,
                            "answer_list": answer_list,
                            "value": answer.value,
                            "label": answer.label,
                            "label_de": answer.label_de,
                        }
                    )
        return (questions_csv, answers_csv)


class ConceptQuestionFactory(DjangoModelFactory):

    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = ConceptQuestion

    question = factory.SubFactory(QuestionFactory)
    concept = factory.SubFactory(ConceptFactory)


class QuestionVariableFactory(factory.django.DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = QuestionVariable

    question = factory.SubFactory(QuestionFactory, name="some-question", sort_id=1)
    variable = factory.SubFactory(VariableFactory, name="some-variable")

    def _to_csv(self) -> dict[str, str]:
        return {
            "study": self.variable.dataset.study.name,
            "dataset": self.variable.dataset.name,
            "variable": self.variable.name,
            "instrument": self.question.instrument.name,
            "question": self.question.name,
        }


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
    study = context_study
    dataset = None
    variable = None
    instrument = None
    question = None

    @factory.post_generation
    def attached_object(self, **kwargs):
        self.study = self.context_study
        fields = {
            "dataset": DatasetFactory(),
            "variable": VariableFactory(),
            "instrument": InstrumentFactory(),
            "question": QuestionFactory(),
        }
        for field in fields:
            if getattr(self, field) is not None:
                return
        object_to_attach_to = choice(fields.keys())
        setattr(self, object_to_attach_to, fields[object_to_attach_to])

    class Meta:
        model = Attachment

    def _to_csv(self) -> dict[str, str]:

        # The order of items here is important
        fields = ("variable", "question", "dataset", "instrument", "study")
        _type = ""
        for field in fields:
            if getattr(self, field) is not None:
                _type = field
                break
        study: StudyFactory = cast(StudyFactory, self.study)
        return {
            "type": _type,
            "study": study.name,
            "dataset": getattr(self.dataset, "name", ""),
            "variable": getattr(self.variable, "name", ""),
            "instrument": getattr(self.instrument, "name", ""),
            "question": getattr(self.question, "name", ""),
            "url": self.url,
            "url_text": self.url_text,
        }


class NewsFactory(DjangoModelFactory):

    class Meta:
        model = News

    content = factory.LazyAttribute(
        lambda _: "\n".join([f"- {FAKE.sentence()}" for _ in range(3)])
    )
    content_de = factory.LazyAttribute(
        lambda _: "\n".join([f"- {FAKE_DE.sentence()}\n" for _ in range(3)])
    )

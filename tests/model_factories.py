# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,protected-access
# type: ignore[override]
# nosec
"""DjangoModelFactories for user model"""

from collections.abc import Iterable
from random import choice, randint
from typing import TYPE_CHECKING, Any, Union, cast
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

    @staticmethod
    def _to_csv(period) -> dict[str, str]:
        return {
            "study": period.study.name,
            "name": period.name,
            "label": period.label,
            "label_de": period.label_de,
            "description": period.description,
            "definition": period.description,
            "description_de": period.description_de,
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

    @staticmethod
    def _to_csv(topic) -> list[dict[str, str]]:
        topics = [
            {
                "study": topic.study.name,
                "name": topic.name,
                "label": topic.label,
                "label_de": topic.label_de,
                "description": topic.description,
                "definition": topic.description,
                "description_de": topic.description_de,
            }
        ]
        while topic.parent:
            topics.append(
                {
                    "study": topic.study.name,
                    "name": topic.name,
                    "label": topic.label,
                    "label_de": topic.label_de,
                    "description": topic.description,
                    "definition": topic.description,
                    "description_de": topic.description_de,
                }
            )
            topic = topic.parent

        return topics[::-1]

    @staticmethod
    def _to_json(concept) -> list[dict[str, any]]:
        output = []
        for field in ["label", "label_de"]:
            topic = concept.topics.first()
            branch = concept
            branch = {
                "title": getattr(topic, field),
                "key": f"topic_{topic.name}",
                "type": "topic",
                "children": [
                    {
                        "title": getattr(concept, field),
                        "key": f"concept_{concept.name}",
                        "type": "concept",
                    }
                ],
            }
            while topic.parent:
                topic = topic.parent
                branch = {
                    "title": getattr(topic, field),
                    "key": f"topic_{topic.name}",
                    "type": "topic",
                    "children": [branch],
                }
            if field == "label":
                branch = {"language": "en", "topics": [branch]}
            else:
                branch = {"language": "de", "topics": [branch]}
            output.append(branch)
        return output


class ConceptFactory(DjangoModelFactory):
    if TYPE_CHECKING:
        id: UUID

    class Meta:
        model = Concept

    class Params:
        study = factory.SubFactory(StudyFactory)
        size = 1
        depth = 0

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
            self.topics.add(
                TopicFactory(study=study, parent__depth=kwargs.get("depth", 0))
            )

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

    @classmethod
    def _to_csv(cls, concept) -> list[dict[str, str]]:
        topics = [cls._EmptyTopic()]
        lines = []
        if concept.topics.count() > 0:
            topics = concept.topics.all()
        for topic in topics:
            lines.append(
                {
                    "study": topic.study.name,
                    "name": concept.name,
                    "label": concept.label,
                    "label_de": concept.label_de,
                    "description": concept.description,
                    "definition": concept.description,
                    "description_de": concept.description_de,
                    "topic": topic.name,
                }
            )
        return lines


class ConceptualDatasetFactory(DjangoModelFactory):

    class Meta:
        model = ConceptualDataset

    study = factory.SubFactory(StudyFactory)
    name = factory.Sequence(lambda n: f"{FAKE.word()}_{n}")
    label = factory.LazyAttribute(lambda _: FAKE.word())
    label_de = factory.LazyAttribute(lambda _: FAKE_DE.word())
    description = factory.LazyAttribute(lambda _: FAKE.paragraphs())
    description_de = factory.LazyAttribute(lambda _: FAKE_DE.paragraphs())

    @staticmethod
    def _to_csv(conceptual_dataset) -> dict[str, str]:
        return {
            "study": conceptual_dataset.study.name,
            "name": conceptual_dataset.name,
            "label": conceptual_dataset.label,
            "label_de": conceptual_dataset.label_de,
            "description": conceptual_dataset.description,
            "definition": conceptual_dataset.description,
            "description_de": conceptual_dataset.description_de,
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

    @staticmethod
    def _to_csv(analysis_unit) -> dict[str, str]:
        return {
            "study": analysis_unit.study.name,
            "name": analysis_unit.name,
            "label": analysis_unit.label,
            "label_de": analysis_unit.label_de,
            "description": analysis_unit.description,
            "definition": analysis_unit.description,
            "description_de": analysis_unit.description_de,
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

    @staticmethod
    def _to_json(dataset) -> list[dict[str, any]]:
        variables = Variable.objects.filter(dataset=dataset)
        lines = []

        for variable in variables:
            lines.append(VariableFactory._variable_to_json(variable))
        return lines

    @staticmethod
    def _to_csv(dataset) -> dict[str, str]:
        if dataset.primary_key == "":
            variable = Variable.objects.filter(dataset=dataset).first()
            if variable:
                dataset.primary_key = variable.name

        return {
            "study": dataset.study.name,
            "name": dataset.name,
            "label": dataset.label,
            "label_de": dataset.label_de,
            "description": dataset.description,
            "definition": dataset.description,
            "description_de": dataset.description_de,
            "analysis_unit": dataset.analysis_unit.name,
            "conceptual_dataset": dataset.conceptual_dataset.name,
            "folder": dataset.folder,
            "primary_key": dataset.primary_key,
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

    @classmethod
    def _to_json(cls, variable):
        return cls._variable_to_json(variable)

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

    @classmethod
    def _to_csv(cls, variable):
        additional_fields = {
            "description": variable.description,
            "description_de": variable.description_de,
            "concept": variable.concept.name,
        }
        return {**cls._variable_to_json(variable), **additional_fields}


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

    @staticmethod
    def _to_csv(publication):
        return {
            "study": publication.study.name,
            "name": publication.name,
            "title": publication.title,
            "author": publication.author,
            "year": publication.year,
            "abstract": publication.abstract,
            "cite": publication.cite,
            "type": publication.type,
            "studies": publication.studies,
            "url": publication.url,
            "doi": publication.doi,
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

    @staticmethod
    def _to_csv(transformation):
        return {
            "origin_study_name": transformation.origin.dataset.study.name,
            "origin_dataset_name": transformation.origin.dataset.name,
            "origin_variable_name": transformation.origin.name,
            "target_study_name": transformation.target.dataset.study.name,
            "target_dataset_name": transformation.target.dataset.name,
            "target_variable_name": transformation.target.name,
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

    @staticmethod
    def _to_csv(instrument):
        _type: dict[str, Any] = cast(dict[str, Any], instrument.type)
        return {
            "study": instrument.study.name,
            "name": instrument.name,
            "label": instrument.label,
            "label_de": instrument.label_de,
            "description": instrument.description,
            "description_de": instrument.description_de,
            "analysis_unit": instrument.analysis_unit.name,
            "period": instrument.period.name,
            "mode": instrument.mode,
            "type": _type["en"],  # pylint: disable=unsubscriptable-object
            "type_de": _type["de"],  # pylint: disable=unsubscriptable-object
            "type_position": _type["position"],  # pylint: disable=unsubscriptable-object
        }

    @classmethod
    def _to_json(cls, instrument):
        instrument_data = cls._to_csv(instrument)
        for field in ["analysis_unit", "description", "description_de"]:
            del instrument_data[field]
        questions = {}
        for question in Question.objects.filter(instrument=instrument):
            items = []
            for item in question.question_items.all():
                items.append(QuestionItemFactory._to_json(item))

            questions[question.name] = {
                "question": question.name,
                "name": question.name,
                "label": question.label,
                "label_de": question.label_de,
                "items": items,
            }
        instrument_data["questions"] = questions
        return instrument_data


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
        if isinstance(extracted, Concept):
            self.concepts_questions.add(
                ConceptQuestionFactory(question=self, concept=extracted)
            )
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

    @staticmethod
    def _to_csv(question) -> tuple[dict[str, str], dict[str, str]]:
        instrument_name = question.instrument.name
        study_name = question.instrument.study.name
        questions_csv = []
        answers_csv = []

        for item in question.question_items.all().order_by("position"):
            _question = {
                "study": study_name,
                "instrument": instrument_name,
                "name": question.name,
                "item": item.name,
                "text": item.label,
                "text_de": item.label_de,
                "instruction": item.instruction,
                "instruction_de": item.instruction_de,
                "description": item.description,
                "description_de": item.description_de,
                "filter": item.input_filter,
                "goto": item.goto,
                "scale": item.scale,
                "answer_list": "",
                "concept": question.concepts_questions.first().concept.name,
            }
            if item.scale == "cat":
                _question["answer_list"] = item.id
                answer_list = item.id
                for answer in item.answers.all():
                    answers_csv.append(
                        {
                            "study": study_name,
                            "instrument": question.instrument.name,
                            "answer_list": answer_list,
                            "value": answer.value,
                            "label": answer.label,
                            "label_de": answer.label_de,
                        }
                    )
            questions_csv.append(_question)
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

    @staticmethod
    def _to_csv(question_variable) -> dict[str, str]:
        return {
            "study": question_variable.variable.dataset.study.name,
            "dataset": question_variable.variable.dataset.name,
            "variable": question_variable.variable.name,
            "instrument": question_variable.question.instrument.name,
            "question": question_variable.question.name,
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

    url = factory.LazyAttribute(lambda _: FAKE.url())
    url_text = factory.LazyAttribute(lambda _: FAKE.sentence())
    context_study = factory.SubFactory(StudyFactory)
    study = context_study
    dataset = None
    variable = None
    instrument = None
    question = None

    @factory.post_generation
    def attached_object(self, create, extracted, **_):
        if not create:
            return
        self.study = self.context_study
        fields = {
            "dataset": DatasetFactory(),
            "variable": VariableFactory(),
            "instrument": InstrumentFactory(),
            "question": QuestionFactory(),
        }
        if not isinstance(extracted, dict):
            extracted = {}

        if all(field in fields for field in extracted):
            for key, value in extracted.items():
                fields[key] = value

        for field in fields:
            if getattr(self, field) is not None:
                return
        object_to_attach_to = choice(fields.keys())
        setattr(self, object_to_attach_to, fields[object_to_attach_to])

    class Meta:
        model = Attachment

    @staticmethod
    def _to_csv(attachment) -> dict[str, str]:

        # The order of items here is important
        fields = ("variable", "question", "dataset", "instrument", "study")
        _type = ""
        for field in fields:
            if getattr(attachment, field) is not None:
                _type = field
                break
        study: StudyFactory = cast(StudyFactory, attachment.study)
        return {
            "type": _type,
            "study": study.name,
            "dataset": getattr(attachment.dataset, "name", ""),
            "variable": getattr(attachment.variable, "name", ""),
            "instrument": getattr(attachment.instrument, "name", ""),
            "question": getattr(attachment.question, "name", ""),
            "url": attachment.url,
            "url_text": attachment.url_text,
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

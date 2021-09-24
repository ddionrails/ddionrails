# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import logging
import uuid
from csv import DictReader
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

from ddionrails.base.helpers.ddionrails_typing import QuestionAnswer
from ddionrails.instruments.models import Instrument, Question
from ddionrails.instruments.models.answer import Answer
from ddionrails.instruments.models.question_item import QuestionItem
from ddionrails.studies.models import Study

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


def question_import(file: Path, study: Study) -> None:
    """Import Questions and QuestionItems from the questions.csv."""
    question_grouper = _group_question_items(study=study)
    next(question_grouper)
    with open(file, "r", encoding="utf8") as csv_file:
        csv_reader = DictReader(csv_file)
        for line in csv_reader:
            question_grouper.send(line)
        question_grouper.send({})


def answer_import(file: Path, study: Study):
    """Import answers and link them to their QuestionItems."""
    answers_file = file
    questions_file = file.parent.joinpath("questions.csv")
    categorical_question_items = QuestionItem.objects.filter(
        scale="cat", question__instrument__study=study
    ).prefetch_related("question", "question__instrument")
    answer_list_answers = _read_answers(answers_file)
    answer_list_answer_ids = _bulk_import_answers(answer_list_answers)
    relations = []
    del answer_list_answers
    with open(questions_file, "r", encoding="utf8") as questions_csv:
        questions_reader = DictReader(questions_csv)
        for question_item in questions_reader:
            if question_item["scale"] != "cat":
                continue
            question_item_object = categorical_question_items.get(
                question__instrument__name=question_item["instrument"],
                question__name=question_item["name"],
                name=question_item["item"],
            )
            question_item_id = question_item_object.generate_id(cache=True)
            for answer_id in answer_list_answer_ids[question_item["answer_list"]]:
                relation = Answer.question_items.through()
                relation.questionitem_id = question_item_id
                relation.answer_id = answer_id
                relations.append(relation)
    Answer.question_items.through.objects.bulk_create(relations, ignore_conflicts=True)


def _bulk_import_answers(
    answers: Dict[str, List[QuestionAnswer]]
) -> Dict[str, List[uuid.UUID]]:
    answer_list_answer_ids: Dict[str, List[uuid.UUID]] = {}
    unique_answer_tuples = set()
    unique_answers: Dict[Tuple[str, str, str], Answer] = {}
    for answer_list, _answers in answers.items():
        answer_list_answer_ids[answer_list] = []
        for answer in _answers:
            answer_tuple: Tuple[str, str, str] = (
                answer["value"],
                answer["label"],
                answer["label_de"],
            )
            if answer_tuple in unique_answer_tuples:
                answer_list_answer_ids[answer_list].append(
                    unique_answers[answer_tuple].id
                )
                continue
            unique_answer_tuples.add(answer_tuple)
            answer_object = Answer(
                value=answer["value"], label=answer["label"], label_de=answer["label_de"]
            )
            answer_object.id = answer_object.generate_id()
            unique_answers[answer_tuple] = answer_object
            answer_list_answer_ids[answer_list].append(answer_object.id)

    Answer.objects.bulk_create(unique_answers.values(), ignore_conflicts=True)
    return answer_list_answer_ids


def _read_answers(file: Path) -> Dict[str, List[QuestionAnswer]]:
    answers: Dict[str, List[QuestionAnswer]] = {}
    with open(file, "r", encoding="utf8") as csv_file:
        csv_reader = DictReader(csv_file)
        for line in csv_reader:
            line["value"] = int(line["value"])
            if line["answer_list"] in answers:
                answers[line["answer_list"]].append(
                    {key: line[key] for key in ["value", "label", "label_de"]}
                )
            else:
                answers[line["answer_list"]] = [
                    {key: line[key] for key in ["value", "label", "label_de"]}
                ]
    return answers


def _group_question_items(study: Study) -> Generator[None, Dict[str, Any], None]:
    question_block = []
    question = yield
    question_block.append(question)

    while question:
        # Questions of a Block have the same name and the same instrument
        if (question["instrument"], question["name"]) != (
            question_block[-1]["instrument"],
            question_block[-1]["name"],
        ):
            _import_question_block(question_block, study)
            question_block = []
        question_block.append(question)
        question = yield
    _import_question_block(question_block, study)
    yield


def _import_question_block(block: List[Dict[str, str]], study: Study):
    instrument = _get_instrument(name=block[0]["instrument"], study=study)
    fields = [
        "label",
        "label_de",
        "description",
        "description_de",
        "instruction",
        "instruction_de",
    ]
    item_specific_fields = ["input_filter", "goto", "scale", "name"]

    main_question, _ = Question.objects.get_or_create(
        name=block[0]["name"], instrument=instrument
    )
    _import_main_question(main_question, fields, block[0])

    fields.extend(item_specific_fields)
    question_items = []
    for position, question in enumerate(block):
        question_item, _ = QuestionItem.objects.get_or_create(
            question=main_question, position=position
        )
        for field in fields:
            setattr(question_item, field, question[_field_mapper(field)])

        question_items.append(question_item)
    QuestionItem.objects.bulk_update(question_items, fields)

    main_question.save()


def _import_main_question(
    question: Question, fields: List[str], metadata: Dict[str, str]
) -> None:
    for field in fields:
        setattr(question, field, metadata[_field_mapper(field)])


def _field_mapper(field: str) -> str:
    """Maps differing field names from csv fields to model fields."""
    fields = {
        "label": "text",
        "label_de": "text_de",
        "input_filter": "filter",
        "name": "item",
    }
    return fields.get(field, field)


@lru_cache(maxsize=100)
def _get_answer(value: int, label: str, label_de: str) -> Answer:
    answer, _ = Answer.objects.get_or_create(value=value, label=label, label_de=label_de)
    return answer


@lru_cache(maxsize=2)
def _get_instrument(study: Study, name: str) -> Instrument:
    """Cache instrument retrieval.

    The cache does not need to be large since questions with the same instrument
    are grouped together in the source file.
    """
    return Instrument.objects.get(name=name, study=study)

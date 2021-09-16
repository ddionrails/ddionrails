# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import logging
from csv import DictReader
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Generator, List, Union

from ddionrails.instruments.models import Instrument, Question
from ddionrails.instruments.models.answer import Answer
from ddionrails.instruments.models.question_item import QuestionItem
from ddionrails.studies.models import Study

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)

answers: Dict[str, List[Dict[str, Union[int, str]]]] = {}


def question_import(file: Path, study: Study) -> None:
    """New question import."""
    answers_path = file.parent.joinpath("answers.csv")
    _read_answers(answers_path)
    question_grouper = _group_question_items(study=study)
    next(question_grouper)
    with open(file, "r", encoding="utf8") as csv_file:
        csv_reader = DictReader(csv_file)
        for line in csv_reader:
            question_grouper.send(line)
        question_grouper.send({})


def _read_answers(file: Path) -> None:
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
    for position, question in enumerate(block):
        question_item = QuestionItem()
        question_item.question = main_question
        question_item.position = position
        for field in fields:
            setattr(question_item, field, question[_field_mapper(field)])
        question_item.label = question["text"]
        question_item.label_de = question["text_de"]

        question_item.save()
        if question_item.scale == "cat":
            _import_question_item_answers(question_item, question["answer_list"])

    main_question.save()


def _import_question_item_answers(question_item, answer_list):
    question_item_answers = answers[answer_list]
    for answer in question_item_answers:
        answer_object = _get_answer(answer["value"], answer["label"], answer["label_de"])
        answer_object.question_items.add(question_item)
        answer_object.save()


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

# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

from collections import namedtuple
from csv import DictReader
from typing import Dict, List, Set, Tuple
from uuid import UUID

from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.instruments.models.item_variable import ItemVariable
from ddionrails.instruments.models.question_variable import QuestionVariable
from ddionrails.studies.models import Study

QuestionRelation = namedtuple("QuestionRelation", ["question", "variable"])
ItemRelation = namedtuple("ItemRelation", ["item", "variable"])
InstrumentRelation = namedtuple("InstrumentRelation", ["instrument", "dataset"])


def question_variable_import(file_path: str, study: Study) -> None:
    """Import relations between Variable and Question model objects."""
    QuestionVariable.objects.filter(variable__dataset__study=study).delete()
    ItemVariable.objects.filter(variable__dataset__study=study).delete()
    Instrument.datasets.through.objects.filter(instrument__study=study).delete()

    instrument_dataset_relations: Set[InstrumentRelation] = set()
    question_variable_relations: set[QuestionRelation] = set()
    item_variable_relations: set[ItemRelation] = set()

    (
        instrument_dataset_relations,
        question_variable_relations,
        item_variable_relations,
    ) = _read_relations(file_path=file_path, study=study)

    if item_variable_relations:
        question_relations, item_relations = _create_question_and_item_relation_objects(
            question_variable_relations, item_variable_relations
        )
        ItemVariable.objects.bulk_create(item_relations)
    else:
        question_relations = _create_question_relation_objects(
            question_variable_relations
        )

    QuestionVariable.objects.bulk_create(question_relations)

    instrument_relations: List[Instrument.datasets.through] = []
    for instrument_relation in instrument_dataset_relations:
        instrument_relations.append(
            Instrument.datasets.through(
                instrument_id=instrument_relation.instrument,
                dataset_id=instrument_relation.dataset,
            )
        )
    Instrument.datasets.through.objects.bulk_create(instrument_relations)


def _create_question_and_item_relation_objects(
    question_relations: Set[QuestionRelation], item_relations: Set[ItemRelation]
) -> Tuple[List[QuestionVariable], List[ItemVariable]]:
    question_relation_objects = []
    item_relation_objects = []
    for question_relation, item_relation in zip(question_relations, item_relations):
        question_relation_objects.append(
            QuestionVariable(
                variable_id=question_relation.variable,
                question_id=question_relation.question,
            )
        )
        item_relation_objects.append(
            ItemVariable(item_id=item_relation.item, variable_id=item_relation.variable)
        )
    return question_relation_objects, item_relation_objects


def _create_question_relation_objects(
    question_relations: Set[QuestionRelation],
) -> List[QuestionVariable]:
    question_relation_objects = []
    for question_relation in question_relations:
        question_relation_objects.append(
            QuestionVariable(
                variable_id=question_relation.variable,
                question_id=question_relation.question,
            )
        )
    return question_relation_objects


def _read_relations(
    file_path: str, study: Study
) -> Tuple[Set[InstrumentRelation], set[QuestionRelation], set[ItemRelation]]:
    datasets: Dict[str, UUID] = {}
    instruments: Dict[str, UUID] = {}
    instrument_dataset_relations: Set[InstrumentRelation] = set()
    question_variable_relations: set[QuestionRelation] = set()
    item_variable_relations: set[ItemRelation] = set()
    with open(file=file_path, mode="r", encoding="utf-8") as csv_file:
        reader = DictReader(csv_file)
        for row in reader:
            if row["instrument"] not in instruments:
                instruments[row["instrument"]] = hash_with_namespace_uuid(
                    study.id, row["instrument"]
                )
            if row["dataset"] not in datasets:
                datasets[row["dataset"]] = hash_with_namespace_uuid(
                    study.id, row["dataset"]
                )
            instrument_dataset_relations.add(
                InstrumentRelation(
                    instruments[row["instrument"]], datasets[row["dataset"]]
                )
            )
            variable_id = hash_with_namespace_uuid(
                datasets[row["dataset"]], row["variable"]
            )
            question_id = hash_with_namespace_uuid(
                instruments[row["instrument"]], row["question"]
            )
            if "item" in row:
                item_id = hash_with_namespace_uuid(question_id, row["item"])
                item_variable_relations.add(ItemRelation(item_id, variable_id))
            question_variable_relations.add(QuestionRelation(question_id, variable_id))

    return (
        instrument_dataset_relations,
        question_variable_relations,
        item_variable_relations,
    )

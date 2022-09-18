# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

from collections import namedtuple
from csv import DictReader
from typing import Dict, List, Set, Tuple
from uuid import UUID

from ddionrails.data.models import Dataset
from ddionrails.imports import imports
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models import Question, QuestionVariable
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.studies.models import Study

QuestionRelation = namedtuple("QuestionRelation", ["question", "variable"])
InstrumentRelation = namedtuple("InstrumentRelation", ["instrument", "dataset"])


def question_variable_import(file_path: str, study: Study) -> None:
    """Import relations between Variable and Question model objects."""
    QuestionVariable.objects.filter(variable__dataset__study=study).delete()
    Instrument.datasets.through.objects.filter(instrument__study=study).delete()

    datasets: Dict[str, UUID] = {}
    instruments: Dict[str, UUID] = {}
    instrument_dataset_relations: Set[InstrumentRelation] = set()
    question_variable_relations: set[QuestionRelation] = set()
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
            question_variable_relations.add(QuestionRelation(question_id, variable_id))
    question_relations: List[QuestionVariable] = []
    for question_relation in question_variable_relations:
        question_relations.append(
            QuestionVariable(
                variable_id=question_relation.variable,
                question_id=question_relation.question,
            )
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

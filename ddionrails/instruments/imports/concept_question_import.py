# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import logging
from csv import DictReader
from typing import Dict, Optional, Set, Tuple

from django.db.transaction import atomic

from ddionrails.concepts.models import Concept
from ddionrails.imports import imports
from ddionrails.instruments.models import ConceptQuestion, Question
from ddionrails.studies.models import Study

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


class ConceptQuestionImport(imports.CSVImport):
    """Imports links between Concepts and Questions

    Reuses the content of questions.csv.
    Both Question and Concept have to already exist.
    """

    content: Set[Tuple[str, str, str, Optional[str]]]

    def read_file(self):
        self.content = set()
        with open(self.file_path(), "r", encoding="utf8") as questions_csv:
            reader = DictReader(questions_csv)
            for row in reader:
                _question = (
                    row.get("study", row.get("study_name", "")),
                    row.get("instrument", row.get("instrument_name", "")),
                    row.get("name", row.get("question_name", "")),
                    row.get("concept", row.get("concept_name", None)),
                )
                if _question[3] == "":
                    continue
                if "" in _question:
                    raise ValueError(
                        (
                            "Expected values in columns: "
                            "study, instrument, name and concept. "
                            f"Got {_question}"
                        )
                    )
                self.content.add(_question)

    @atomic
    def execute_import(self):
        studies: Dict[str, Study] = {}
        for concept_question_data in self.content:
            if concept_question_data[0] not in studies.keys():
                try:
                    study = Study.objects.get(name=concept_question_data[0])
                    studies[study.name] = study
                except Study.DoesNotExist:
                    continue
            try:
                concept_question = Question.objects.get(
                    instrument__study=studies[concept_question_data[0]],
                    instrument__name=concept_question_data[1],
                    name=concept_question_data[2],
                )
                concept = Concept.objects.get(name=concept_question_data[3])
            except BaseException as error:
                raise type(error)(
                    f"Could not import ConceptQuestion: {concept_question_data}"
                )
            ConceptQuestion.objects.get_or_create(
                question=concept_question, concept=concept
            )

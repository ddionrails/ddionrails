# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import json
import logging
from collections import OrderedDict
from csv import DictReader
from pathlib import Path
from typing import Dict, Optional

from django.db.transaction import atomic

from ddionrails.concepts.models import AnalysisUnit, Concept, Period
from ddionrails.data.models import Variable
from ddionrails.imports import imports
from ddionrails.imports.helpers import download_image, store_image

from .models import ConceptQuestion, Instrument, Question, QuestionImage, QuestionVariable

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


class InstrumentImport(imports.Import):
    """Import a single Instrument and its containing questions.

    Is called with a single instrument JSON file.
    Also imports associated Periods and analysis_units, if they are not
    already present.
    """

    content: str

    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_instrument(self.name, self.content)

    def _import_instrument(self, name, content):
        instrument, _ = Instrument.objects.get_or_create(study=self.study, name=name)

        # add period relation to instrument
        period_name = content.get("period", "none")
        # Workaround for two ways to name period: period, period_name
        # => period_name
        if period_name == "none":
            period_name = content.get("period_name", "none")

        # Workaround for periods coming in as float, w.g. 2001.0
        try:
            period_name = str(int(period_name))
        except ValueError:
            period_name = str(period_name)
        period = Period.objects.get_or_create(name=period_name, study=self.study)[0]
        instrument.period = period

        # add analysis_unit relation to instrument
        analysis_unit_name = content.get("analysis_unit", "none")
        if analysis_unit_name == "none":
            analysis_unit_name = content.get("analysis_unit_name", "none")
        analysis_unit = AnalysisUnit.objects.get_or_create(
            name=analysis_unit_name, study=self.study
        )[0]
        instrument.analysis_unit = analysis_unit

        for _name, _question in content["questions"].items():
            question, _ = Question.objects.get_or_create(
                name=_question["question"], instrument=instrument
            )
            question.sort_id = int(_question.get("sn", 0))
            question.label = _question.get("label", _question.get("text", _name))
            question.label_de = _question.get("label_de", _question.get("text_de", ""))
            question.description = _question.get("description", "")
            question.description_de = _question.get("description_de", "")
            question.items = _question.get("items", list)
            question.save()
            image_data = _question.get("image", None)
            if image_data:
                self.question_image_import(question, image_data)

        instrument.label = content.get("label", "")
        instrument.label_de = content.get("label_de", "")
        instrument.description = content.get("description", "")
        instrument.description_de = content.get("description_de", "")
        instrument.save()

    def question_image_import(self, question: Question, image_data: Dict[str, str]):
        """Load and save the images of a Question

        Loads and saves up to two image files given their location by url.

        Args:
            question: The associated Question Object
            image_data: Contains "url" and/or "url_de" keys to locate image files.
                        Optionally contains "label" and/or "label_de" to add a label
                        to the corresponding images.
        """

        images = list()

        if "url" in image_data:
            images.append(
                self._question_image_import_helper(
                    question,
                    url=image_data["url"],
                    label=image_data.get("label", None),
                    language="en",
                )
            )
        if "url_de" in image_data:
            images.append(
                self._question_image_import_helper(
                    question,
                    url=image_data["url_de"],
                    label=image_data.get("label_de", None),
                    language="de",
                )
            )

        for image in images:
            if image is not None:
                image.save()

    @staticmethod
    def _question_image_import_helper(
        question: Question, url: str, label: Optional[str], language: str
    ) -> Optional[QuestionImage]:
        """Create a QuestionImage Object, load and store Image file inside it

        Args:
            question: The associated Question Object
            url: Location of the image to be loaded
            label: Is stored in the QuestionImage label field
            language: Is stored in the QuestionImage language field
        Returns:
            The QuestionImage created with loaded image.
            If the image could not be loaded, this will return None.
            QuestionImage is not written to the database here.
        """
        question_image = QuestionImage()
        instrument = question.instrument
        path = [instrument.study.name, instrument.name, question.name]
        _image = download_image(url)
        suffix = Path(url).suffix
        if label is None:
            label = "Screenshot"
        if _image is None:
            return None
        image, _ = store_image(file=_image, name=label + suffix, path=path)
        question_image.question = question
        question_image.image = image
        question_image.label = label
        question_image.language = language
        return question_image


class QuestionVariableImport(imports.CSVImport):
    def execute_import(self):
        for link in self.content:
            self._import_link(link)

    def _import_link(self, link):
        try:
            question = self._get_question(link)
            variable = self._get_variable(link)
            QuestionVariable.objects.get_or_create(question=question, variable=variable)
        except BaseException as error:
            raise type(error)(f"Could not import QuestionVariable: {link}")

    @staticmethod
    def _get_question(link):
        question = (
            Question.objects.filter(
                instrument__study__name=link.get("study", link.get("study_name"))
            )
            .filter(instrument__name=link.get("instrument", link.get("instrument_name")))
            .get(name=link.get("question", link.get("question_name")))
        )
        return question

    @staticmethod
    def _get_variable(link):
        variable = (
            Variable.objects.filter(
                dataset__study__name=link.get("study", link.get("study_name"))
            )
            .filter(dataset__name=link.get("dataset", link.get("dataset_name")))
            .filter(name=link.get("variable", link.get("variable_name")))
            .first()
        )
        return variable


class ConceptQuestionImport(imports.CSVImport):
    """Imports links between Concepts and Questions

    Reuses the content of questions.csv.
    Both Question and Concept have to already exist.
    """

    def read_file(self):
        self.content: Dict[str, str] = dict()
        with open(self.file_path(), "r") as questions_csv:
            reader = DictReader(questions_csv)
            for row in reader:
                # No concept; nothing to import for this question
                if not row.get("concept", row.get("concept_name")):
                    continue
                _question = (
                    row.get("study", row.get("study_name")),
                    row.get("instrument", row.get("instrument_name")),
                    row.get("name", row.get("question_name")),
                )
                self.content[_question] = row.get("concept", row.get("concept_name"))

    @atomic
    def execute_import(self):
        for question, concept in self.content.items():
            self._import_link(
                {
                    "study": question[0],
                    "instrument": question[1],
                    "question": question[2],
                    "concept": concept,
                }
            )

    def _import_link(self, link):
        try:
            question = self._get_question(link)
            concept = Concept.objects.get(name=link.get("concept"))
        except BaseException as error:
            raise type(error)(f"Could not import ConceptQuestion: {link}")
        ConceptQuestion.objects.get_or_create(question=question, concept=concept)

    @staticmethod
    def _get_question(element):
        study = element.get("study")
        instrument = element.get("instrument")
        question = element.get("question")

        question_object = Question.objects.get(
            instrument__study__name=study, instrument__name=instrument, name=question
        )
        return question_object

# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.instruments app """

import logging

from ddionrails.data.models import Variable
from ddionrails.imports import imports
from ddionrails.instruments.models import Question, QuestionVariable

logging.config.fileConfig("logging.conf")  # type: ignore
logger = logging.getLogger(__name__)


class QuestionVariableImport(imports.CSVImport):
    """Import relations between Variable and Question model objects."""

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

# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.concepts app """

import json
import logging

from ddionrails.imports import imports

from .forms import (
    AnalysisUnitForm,
    ConceptForm,
    ConceptualDatasetForm,
    PeriodForm,
    TopicForm,
)
from .models import Topic

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class TopicImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = TopicForm

    def process_element(self, element):
        parent_name = element.get("parent_name", None)
        if parent_name:
            try:
                element["parent"] = Topic.objects.get_or_create(
                    study=self.study, name=parent_name
                )[0].id
            except:
                logger.error(f'Could not import parent for: "{element}"')
        element["study"] = self.study.id
        return element


class TopicJsonImport(imports.Import):
    def execute_import(self):
        self.content = json.JSONDecoder().decode(self.content)
        self._import_topic_list()

    def _import_topic_list(self):
        study = self.study
        study.topic_languages = ["de", "en"]
        study.save()
        body = self.content
        study.set_topiclist(body)


class ConceptImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = ConceptForm

    def import_element(self, element):
        new_concept = super().import_element(element)
        topic_name = element.get("topic_name", None)
        if topic_name and new_concept:
            try:
                topic = Topic.objects.get(name=topic_name, study=self.study)
                topic.concepts.add(new_concept)
            except:
                logger.error(
                    f'Could not link concept "{new_concept.name}"" to topic "{topic_name}"'
                )
        return new_concept


class AnalysisUnitImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = AnalysisUnitForm


class PeriodImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = PeriodForm

    def process_element(self, element):
        element["study"] = self.study.id
        return element


class ConceptualDatasetImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = ConceptualDatasetForm

    def process_element(self, element):
        element["study"] = self.study.id
        return element

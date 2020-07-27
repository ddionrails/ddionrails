# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.concepts app """

import json
import logging

from django.db.transaction import atomic

from ddionrails.concepts.models import Concept
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

    @atomic
    def execute_import(self):
        super().execute_import()

    def import_element(self, element):
        concept_name = element.get("name", "")
        if not concept_name:
            return None
        concept, _ = Concept.objects.get_or_create(name=concept_name)
        concept.label = element.get("label", "")
        concept.label_de = element.get("label_de", "")
        concept.save()
        topic_name = element.get("topic", element.get("topic_name"))
        if topic_name:
            try:
                topic = Topic.objects.get(name=topic_name, study=self.study)
                topic.concepts.add(concept)
            except Topic.DoesNotExist:
                logger.error(
                    (
                        'Could not link concept "%s" to topic "%s"',
                        concept.name,
                        topic_name,
                    )
                )
        return concept


class AnalysisUnitImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = AnalysisUnitForm

    def process_element(self, element):
        element["study"] = self.study.id
        return element


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

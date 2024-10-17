# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.concepts app """

import json
from csv import DictReader
from pathlib import Path
from typing import Optional, Union

from django.db.transaction import atomic

from ddionrails.concepts.models import Concept, ConceptualDataset
from ddionrails.imports import imports
from ddionrails.imports.helpers import hash_with_base_uuid
from ddionrails.studies.models import Study

from .forms import AnalysisUnitForm, ConceptForm, PeriodForm, TopicForm
from .models import Topic


class TopicImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = TopicForm

    def import_element(self, element):
        study = element.get("study", element.get("study_name"))
        try:
            study_object = Study.objects.get(name=study)
        except Study.DoesNotExist as error:
            raise type(error)(f"Study {study} does not exist: {str(error)}")
        name = element.get("name", element.get("topic_name"))
        parent = element.get("parent", element.get("parent_name"))
        if parent:
            parent_object, _ = Topic.objects.get_or_create(
                name=parent, study=study_object
            )
        else:
            parent_object = None
        topic, _ = Topic.objects.get_or_create(name=name, study=study_object)
        topic.parent = parent_object
        topic.label = element.get("label")
        topic.label_de = element.get("label_de")
        topic.description = element.get("description")
        topic.description_de = element.get("description_de")
        topic.save()


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


def concept_import(file_path: Union[Path, str], study: Optional[Study] = None):
    """Import Conceptual Dataset Metadata."""
    with open(file_path, "r", encoding="utf8") as file:
        reader = DictReader(file)
        concepts = []
        concepts_to_create = set()
        relations = []
        fields_to_update = ["label", "label_de"]
        concept_objects = {concept.name: concept for concept in Concept.objects.all()}
        topic_objects = {topic.name: topic for topic in Topic.objects.filter(study=study)}
        for line in reader:
            concept_name = line.get("name", "")
            if not concept_name:
                continue
            if concept_name in concept_objects:
                concept = concept_objects[concept_name]
            else:
                concept = Concept()
                concept.id = hash_with_base_uuid(  # pylint: disable=C0103
                    "concept:" + concept_name, cache=False
                )
                concept.name = concept_name
                concept.label = line.get("label", "")
                concept.label_de = line.get("label_de", "")
                concepts_to_create.add(concept)
            if (
                concept.label != line.get("label", "")
                or concept.label_de != line.get("label_de", "")
            ) and concept_name in concept_objects:
                concept.label = line.get("label", "")
                concept.label_de = line.get("label_de", "")
                concepts.append(concept)

            topic_name = line.get("topic", line.get("topic_name"))
            if concept_name == "_pgen_pgfamstd":
                print(line)
            if str(concept.id) == "a688696e-5b11-512d-bb4c-d82e84cb0865":
                print(line)
            if topic_name:
                topic = topic_objects[topic_name]
                relations.append(
                    Concept.topics.through(
                        concept_id=concept.id,
                        topic_id=topic.id,
                    )
                )

        print("bulk_update")
        Concept.objects.bulk_update(concepts, fields_to_update)
        Concept.objects.bulk_create(concepts_to_create)
        print("update_topics")
        Concept.topics.through.objects.bulk_create(relations, ignore_conflicts=True)


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


@atomic
def conceptual_dataset_import(file_path: Union[Path, str], study: Optional[Study] = None):
    """Import Conceptual Dataset Metadata."""
    with open(file_path, "r", encoding="utf8") as file:
        reader = DictReader(file)
        conceptual_datasets = []
        fields_to_update = ["label", "label_de", "description", "description_de"]
        for line in reader:
            conceptual_dataset, _ = ConceptualDataset.objects.get_or_create(
                study=study, name=line["name"]
            )
            for key in fields_to_update:
                setattr(conceptual_dataset, key, line.get(key, ""))
            conceptual_datasets.append(conceptual_dataset)
        ConceptualDataset.objects.bulk_update(conceptual_datasets, fields_to_update)

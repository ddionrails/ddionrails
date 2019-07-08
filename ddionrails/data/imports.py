# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.data app """

import json
import logging
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist

from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.imports import imports

from .forms import DatasetForm, VariableForm
from .models import Dataset, Transformation, Variable

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class DatasetJsonImport(imports.Import):
    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_dataset(self.name, self.content)

    def _import_dataset(self, name, content):
        import_dict = dict(study=self.study, name=name)
        dataset = Dataset.get_or_create(import_dict)
        sort_id = 0
        if content.__class__ == list:
            for var in content:
                self._import_variable(var, dataset, sort_id)
        else:
            for name, var in content.items():
                self._import_variable(var, dataset, sort_id)

    def _import_variable(self, var, dataset, sort_id):
        name = var["variable"]
        import_dict = dict(name=var["variable"].lower(), dataset=dataset)
        variable = Variable.get_or_create(import_dict)
        sort_id += 1
        variable.sort_id = sort_id
        variable.label = var.get("label", name)
        variable.label_de = var.get("label_de", name)
        if "statistics" in var:
            statistics = {
                key: value
                for key, value in zip(
                    var["statistics"]["names"], var["statistics"]["values"]
                )
            }
            variable.statistics = statistics
        if "categories" in var:
            values = var["categories"].get("values")
            if values and len(values) > 0:
                variable.categories = var["categories"]
        variable.scale = var.get("scale", "")
        variable.save()


class DatasetImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = DatasetForm

    def import_element(self, element: OrderedDict):
        # TODO: Workaround
        if "dataset_name" not in element.keys():
            element["dataset_name"] = element.get("name")

        try:
            self._import_dataset_links(element)
        except:
            logger.error(f'Failed to import dataset "{element["dataset_name"]}"')

    def _import_dataset_links(self, element: OrderedDict):
        dataset = Dataset.objects.get(study=self.study, name=element["dataset_name"])
        period_name = element.get("period_name", "none")
        dataset.period = Period.objects.get_or_create(study=self.study, name=period_name)[
            0
        ]
        analysis_unit_name = element.get("analysis_unit_name", "none")
        dataset.analysis_unit = AnalysisUnit.objects.get_or_create(
            name=analysis_unit_name
        )[0]
        conceptual_dataset_name = element.get("conceptual_dataset_name", "none")
        dataset.conceptual_dataset = ConceptualDataset.objects.get_or_create(
            name=conceptual_dataset_name
        )[0]
        dataset.boost = float(element.get("boost", 1))
        dataset.label = element.get("label", "")
        dataset.description = element.get("description", "")
        dataset.save()


class VariableImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    def import_element(self, element):
        # TODO: Workaround
        if "variable_name" not in element.keys():
            element["variable_name"] = element.get("name")

        try:
            self._import_variable_links(element)
        except:
            variable = element.get("variable_name")
            dataset = element.get("dataset_name")
            logger.error(
                f'Failed to import variable "{variable}" from dataset "{dataset}"'
            )

    def _import_variable_links(self, element):
        dataset = Dataset.objects.get(study=self.study, name=element["dataset_name"])
        variable = Variable.objects.get(dataset=dataset, name=element["variable_name"])
        concept_name = element.get("concept_name", "").lower()
        if concept_name != "":
            concept = Concept.objects.get_or_create(name=concept_name)[0]
            variable.concept = concept
        variable.description = element.get("description", "")
        variable.description_long = element.get("description_long", "")
        variable.image_url = element.get("image_url", "")
        variable.save()


class TransformationImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    def import_element(self, element):
        try:
            Transformation.goc_by_name(
                element["origin_study_name"],
                element["origin_dataset_name"],
                element["origin_variable_name"],
                element["target_study_name"],
                element["target_dataset_name"],
                element["target_variable_name"],
            )
        except ObjectDoesNotExist:
            origin_variable = f"{element['origin_study_name']}/{element['origin_dataset_name']}/{element['origin_variable_name']}"
            target_variable = f"{element['target_study_name']}/{element['target_dataset_name']}/{element['target_variable_name']}"
            logger.error(
                f'Failed to import transformation from variable"{origin_variable}" to variable "{target_variable}"'
            )

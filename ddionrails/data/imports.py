# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.data app """

import json
import logging
from collections import OrderedDict
from csv import DictReader
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Union

from django.core.exceptions import ObjectDoesNotExist

from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.imports import imports
from ddionrails.imports.helpers import download_image, store_image

from .forms import DatasetForm, VariableForm
from .models import Dataset, Transformation, Variable

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


class DatasetJsonImport(imports.Import):
    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_dataset(self.name, self.content)

    def _import_dataset(self, name, content: Union[Dict, List]):
        dataset, _ = Dataset.objects.get_or_create(study=self.study, name=name)
        sort_id = 0
        if isinstance(content, dict):
            content = list(content.values())
        for var in content:
            self._import_variable(var, dataset, sort_id)
            sort_id += 1

    @staticmethod
    def _import_variable(var, dataset, sort_id):
        name = var.get("name", var.get("variable"))
        variable, _ = Variable.objects.get_or_create(name=name, dataset=dataset)
        variable.sort_id = sort_id
        variable.label = var.get("label", name)
        variable.label_de = var.get("label_de", name)
        if "statistics" in var:
            if "names" in var["statistics"]:
                statistics = dict(
                    zip(var["statistics"]["names"], var["statistics"]["values"])
                )
            else:
                statistics = var["statistics"]
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
            LOGGER.error(f'Failed to import dataset "{element["dataset_name"]}"')

    def _import_dataset_links(self, element: OrderedDict):
        dataset = Dataset.objects.get(study=self.study, name=element["dataset_name"])
        period_name = element.get("period_name", "none")
        dataset.period = Period.objects.get_or_create(study=self.study, name=period_name)[
            0
        ]
        analysis_unit_name = element.get("analysis_unit_name", "none")
        dataset.analysis_unit = AnalysisUnit.objects.get_or_create(
            study=self.study, name=analysis_unit_name
        )[0]
        conceptual_dataset_name = element.get("conceptual_dataset_name", "none")
        dataset.conceptual_dataset = ConceptualDataset.objects.get_or_create(
            study=self.study, name=conceptual_dataset_name
        )[0]
        dataset.label = element.get("label", "")
        dataset.description = element.get("description", "")
        dataset.save()


class VariableImport(imports.CSVImport):
    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    def import_element(self, element):
        variable_metadata = element
        # TODO: Workaround for outdated input field name.
        if "variable_name" not in variable_metadata.keys():
            variable_metadata["variable_name"] = variable_metadata.get("name")

        # This basically dropped variables in "silence" when there was a problem.
        # Incomplete imports are highly undesirable.
        # The exceptions handling should remain here for a while till it is clear
        # what exceptions were actually meant to be handled here.
        try:
            self._import_variable(variable_metadata)
        except BaseException as error:
            variable = variable_metadata.get("variable_name")
            dataset = variable_metadata.get("dataset_name")

            raise type(error)(
                f'Failed to import variable "{variable}" from dataset "{dataset}"'
            )

    def _import_variable(self, element):
        dataset = Dataset.objects.get(study=self.study, name=element["dataset_name"])
        variable = Variable.objects.get(dataset=dataset, name=element["variable_name"])
        concept_name = element.get("concept_name", "")
        if concept_name != "":
            concept = Concept.objects.get(name=concept_name)
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
            origin_variable = (
                f"{element['origin_study_name']}/"
                f"{element['origin_dataset_name']}/"
                f"{element['origin_variable_name']}"
            )
            target_variable = (
                f"{element['target_study_name']}/"
                f"{element['target_dataset_name']}/"
                f"{element['target_variable_name']}"
            )
            LOGGER.error(
                (
                    "Failed to import transformation from variable"
                    f'"{origin_variable}" to variable "{target_variable}"'
                )
            )


class VariableImageImport:
    """Store images that can be linked to existing variables."""

    variables_images: Optional[List[Dict[str, str]]]

    def __init__(self, file_path: Union[str, Path]):
        try:
            with open(file_path, "r") as csv_images:
                self.variables_images = list(DictReader(csv_images))
        except FileNotFoundError:
            self.variables_images = None
        super().__init__()

    def image_import(self):
        """Import all images consecutively."""
        if self.variables_images is None:
            return None
        for variable_data in self.variables_images:
            dataset = self._get_dataset(variable_data["study"], variable_data["dataset"])
            variable = Variable.objects.get(
                name=variable_data["variable"], dataset=dataset.id
            )
            self._image_import(variable, variable_data)
        return None

    @staticmethod
    @lru_cache()
    def _get_dataset(study_name: str, dataset_name: str) -> Dataset:
        """Cache results for Dataset lookups."""
        return Dataset.objects.get(study__name=study_name, name=dataset_name)

    @staticmethod
    def _image_import(variable: Variable, data: Dict[str, str]):
        """Load and store images for a single variable."""
        # Folder structure; location to store the image.
        path = [
            variable.dataset.study.name,
            "datasets",
            variable.dataset.name,
            variable.name,
        ]
        for image_key in {"url", "url_de"}.intersection(data.keys()):
            suffix = Path(data[image_key]).suffix
            _image_file = download_image(data[image_key])
            if "de" in image_key:
                variable.image_de, _ = store_image(
                    file=_image_file, name=variable.label_de + suffix, path=path
                )
            else:
                variable.image, _ = store_image(
                    file=_image_file, name=variable.label + suffix, path=path
                )
        variable.save()

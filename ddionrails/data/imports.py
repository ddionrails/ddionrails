# -*- coding: utf-8 -*-

"""Importer classes for ddionrails.data app"""

import json
import re
from collections import OrderedDict
from csv import DictReader
from functools import lru_cache
from itertools import permutations
from pathlib import Path

from django.db.models import Q
from django.db.transaction import atomic

from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.data.models.transformation import Sibling
from ddionrails.imports import imports
from ddionrails.imports.helpers import hash_with_base_uuid, hash_with_namespace_uuid
from ddionrails.studies.models import Study

from .forms import DatasetForm, VariableForm
from .models import Dataset, Transformation, Variable


class DatasetJsonImport(imports.Import):
    """Import Variable data from JSON files."""

    def execute_import(self):
        content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(self.content)
        if isinstance(content, dict):
            content = list(content.values())
        sort_id = 0
        datasets = {}
        variable_names = set()
        for var in content:
            if var["dataset"] not in datasets:
                dataset, _ = Dataset.objects.get_or_create(
                    study=self.study, name=var["dataset"]
                )
                datasets[var["dataset"]] = dataset
            variable_names.add(var["variable"])
        existing_variables = {
            variable.name
            for variable in Variable.objects.filter(
                dataset__name__in=list(datasets.keys()),
            )
        }
        variables_to_create = []
        variables_to_update = []
        for var in content:
            variable = self._import_variable(var, sort_id, datasets[var["dataset"]])
            if var["variable"] in existing_variables:
                variables_to_update.append(variable)
            else:
                variables_to_create.append(variable)
            sort_id += 1
        Variable.objects.bulk_update(
            variables_to_update,
            fields=("sort_id", "label", "label_de", "statistics", "categories", "scale"),
        )
        Variable.objects.bulk_create(variables_to_create)

    @staticmethod
    def _import_variable(var, sort_id, dataset):
        dataset_id = dataset.id
        name = var.get("name", var.get("variable"))
        variable = Variable(name=name, dataset=dataset)
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

        variable.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            dataset_id, var["variable"], cache=False
        )

        return variable


class DatasetImport(imports.CSVImport):
    """Import Dataset data"""

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = DatasetForm

    def import_element(self, element: OrderedDict):
        if "name" not in element.keys():
            element["name"] = element.get("dataset_name")

        self._import_dataset_links(element)

    def _import_dataset_links(self, element: OrderedDict):
        dataset, _ = Dataset.objects.get_or_create(
            study=self.study, name=element.get("name")
        )
        period_name = element.get("period", element.get("period_name", "none"))
        dataset.period = Period.objects.get_or_create(study=self.study, name=period_name)[
            0
        ]
        analysis_unit_name = element.get(
            "analysis_unit", element.get("analysis_unit_name", "none")
        )
        dataset.analysis_unit = AnalysisUnit.objects.get_or_create(
            study=self.study, name=analysis_unit_name
        )[0]
        conceptual_dataset = element.get(
            "conceptual_dataset", element.get("conceptual_dataset_name", "none")
        )
        dataset.conceptual_dataset = ConceptualDataset.objects.get_or_create(
            study=self.study, name=conceptual_dataset
        )[0]
        dataset.folder = element.get("folder", "")
        primary_key = element.get("primary_key", "").strip().split(" ")
        if "" in primary_key:
            primary_key.remove("")
        dataset.primary_key = primary_key
        dataset.label = element.get("label", "")
        dataset.label_de = element.get("label_de", "")
        dataset.description = element.get("description", "")
        dataset.save()


class VariableImport(imports.CSVImport):
    """Import Variable data from csv file."""

    harmonized_suffix = re.compile(r".*_h$")
    is_harmonized_suffix = re.compile(r".*_v\d+$")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = VariableForm

    def import_element(self, element):
        variable_metadata = element
        if "name" not in variable_metadata.keys():
            variable_metadata["name"] = variable_metadata.get("variable_name")

        # This basically dropped variables in "silence" when there was a problem.
        # Incomplete imports are highly undesirable.
        # The exceptions handling should remain here for a while till it is clear
        # what exceptions were actually meant to be handled here.
        self._import_variable(variable_metadata)
        try:
            ...
        except BaseException as error:
            variable = variable_metadata.get("name")
            dataset = variable_metadata.get("dataset", element.get("dataset_name"))
            raise type(error)(
                f'Failed to import variable "{variable}" from dataset "{dataset}"'
            ) from error

    def execute_import(self):
        for row in self.content:
            self.import_element(row)

    def _import_variable(self, element):
        dataset = Dataset.objects.get(
            study=self.study, name=element.get("dataset", element.get("dataset_name"))
        )
        variable, _ = Variable.objects.get_or_create(
            dataset=dataset, dataset__study=self.study, name=element["name"]
        )
        concept_name = element.get("concept", element.get("concept_name", ""))
        if concept_name != "":
            concept = Concept.objects.get(name=concept_name)
            variable.concept = concept
        if dataset.period.name == "0":
            variable.long_variable = True
            if self.harmonized_suffix.match(variable.name):
                variable.harmonization = True
            if self.is_harmonized_suffix.match(variable.name):
                variable.is_harmonized = True
        variable.description = element.get("description", "")
        variable.description_de = element.get("description_de", "")
        variable.description_long = element.get("description_long", "")
        variable.image_url = element.get("image_url", "")
        variable.statistics_type = element.get("type", "")
        variable.statistics_flag = element.get("statistics", "False") == "True"
        if not variable.label:
            variable.label = element.get("label", "")
        if not variable.label_de:
            variable.label_de = element.get("label_de", "")
        variable.save()


@lru_cache(30000)
def _get_element_id(study_name, dataset_name, variable_name):
    return hash_with_namespace_uuid(
        hash_with_namespace_uuid(
            _get_study_id(study_name),
            dataset_name,
            cache=True,
        ),
        variable_name,
        cache=True,
    )


@lru_cache(100)
def _get_study_id(study__name: str):
    return hash_with_base_uuid(study__name)


class TransformationImport(imports.CSVImport):
    """Import Object relations from the transformations.csv file."""

    @atomic
    def execute_import(self):
        existing_transformations = {
            (transformation.origin.id, transformation.target.id)
            for transformation in Transformation.objects.filter(
                Q(origin__dataset__study=self.study)
                | Q(target__dataset__study=self.study)
            )
        }
        transformations = []

        for element in self.content:
            origin_id = _get_element_id(
                element["origin_study_name"],
                element["origin_dataset_name"],
                element["origin_variable_name"],
            )
            target_id = _get_element_id(
                element["target_study_name"],
                element["target_dataset_name"],
                element["target_variable_name"],
            )
            if (origin_id, target_id) in existing_transformations:
                continue
            transformations.append(
                Transformation(origin_id=origin_id, target_id=target_id)
            )
        if transformations:
            Transformation.objects.bulk_create(transformations, batch_size=5000)


def variables_images_import(file: Path, study: Study) -> None:
    "Initiate imports of all question images"
    if not file.exists():
        return
    with open(file, "r", encoding="utf8") as csv:
        reader = DictReader(csv)
        variables: list[Variable] = []
        for index, row in enumerate(reader):
            try:
                variable = Variable.objects.get(
                    dataset__study=study,
                    dataset__name=row["dataset"],
                    name=row["variable"],
                )
            except Variable.DoesNotExist as error:
                raise Variable.DoesNotExist(f"Variable {row} does not exist") from error
            variable.images = {
                "de": row["url_de"],
                "en": row["url"],
            }
            variables.append(variable)
            if index % 1000:
                Variable.objects.bulk_update(variables, ["images"])
                variables = []
        if variables:
            Variable.objects.bulk_update(variables, ["images"])


@atomic
def siblings_generation(_: Path, study: Study):
    """Create relations between variables related to the same harmonized variable

    This is unique to variables created at SOEP

    """
    Sibling.objects.filter(sibling_a__dataset__study=study).delete()

    long_variables = Variable.objects.filter(
        dataset__period__name="0", dataset__study=study, name__endswith="_h"
    ).prefetch_related("origin_variables", "target_variables")
    siblings: list[Sibling] = []

    harmonized_suffix = re.compile(r".*_v/d+$")

    for long_variable in long_variables.all():
        target_transformations = long_variable.target_variables.all().distinct()
        origin_transformations = long_variable.origin_variables.all().distinct()
        target_variables = [variable.target for variable in target_transformations]
        origin_variables_variables = [
            variable.origin for variable in origin_transformations
        ]
        for variables in (target_variables, origin_variables_variables):
            if not variables:
                continue
            for pair in permutations(variables, 2):
                sibling_relation = Sibling()
                sibling_relation.sibling_a, sibling_relation.sibling_b = pair

                if harmonized_suffix.search(pair[0].name) or harmonized_suffix.search(
                    pair[1].name
                ):
                    continue
                siblings.append(sibling_relation)

    Sibling.objects.bulk_create(siblings)

# -*- coding: utf-8 -*-

""" Importer classes for ddionrails.data app """

import json
import logging
from collections import OrderedDict

from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.imports import imports

from .forms import DatasetForm, VariableForm
from .models import Dataset, Variable

logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)


class DatasetJsonImport(imports.Import):
    def execute_import(self):
        self.content = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            self.content
        )
        self._import_dataset(self.name, self.content)

    def _import_dataset(self, name, content):
        dataset, _ = Dataset.objects.get_or_create(study=self.study, name=name)
        sort_id = 0
        if content.__class__ == list:
            for var in content:
                self._import_variable(var, dataset, sort_id)
        else:
            for name, var in content.items():
                self._import_variable(var, dataset, sort_id)

    def _import_variable(self, var, dataset, sort_id):
        name = var["variable"]
        variable, _ = Variable.objects.get_or_create(name=name, dataset=dataset)
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

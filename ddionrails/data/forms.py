# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" ModelForms for ddionrails.data app """

from django import forms

from ddionrails.concepts.models import Concept
from ddionrails.data.models import Dataset, Variable


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = (
            "name",
            "label",
            "description",
            "study",
            "conceptual_dataset",
            "period",
            "analysis_unit",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["name"] = self.data["dataset_name"]


class VariableForm(forms.ModelForm):
    class Meta:
        model = Variable
        fields = (
            "name",
            "label",
            "description",
            "concept",
            "dataset",
            "sort_id",
            "image_url",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["name"] = self.data["variable_name"]
        _dataset, _ = Dataset.objects.get_or_create(
            name=self.data["dataset_name"], study=self.data["study_object"]
        )
        self.data["dataset"] = _dataset.id
        if self.data.get("concept_name", "") == "":
            self.data["concept"] = None
        else:
            _concept, _ = Concept.objects.get_or_create(name=self.data["concept_name"])
            self.data["concept"] = _concept.id

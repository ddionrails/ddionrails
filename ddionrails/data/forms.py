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
            "boost",
            "conceptual_dataset",
            "period",
            "analysis_unit",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["boost"] = float(self.data["boost"])
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
        self.data["dataset"] = Dataset.get_or_create(
            dict(name=self.data["dataset_name"], study=self.data["study_object"])
        ).pk
        if self.data.get("concept_name", "") == "":
            self.data["concept"] = None
        else:
            self.data["concept"] = Concept.get_or_create(
                dict(name=self.data["concept_name"].lower())
            ).pk

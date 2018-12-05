from django import forms

from concepts.models import Concept
from data.models import Dataset, Variable
from ddionrails.helpers import lower_dict_names
from studies.models import Study


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
        self.data["cs_name"] = self.data["dataset_name"]
        self.data["name"] = self.data["dataset_name"].lower()


class VariableForm(forms.ModelForm):

    class Meta:
        model = Variable
        fields = ("name", "label", "description", "concept", "dataset", "sort_id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["cs_name"] = self.data["variable_name"]
        self.data["name"] = self.data["variable_name"].lower()
        self.data["dataset"] = Dataset.get_or_create(dict(
            name=self.data["dataset_name"].lower(),
            study=self.data["study_object"],
        )).pk
        if self.data.get("concept_name", "") == "":
            self.data["concept"] = None
        else:
            self.data["concept"] = Concept.get_or_create(dict(
                name=self.data["concept_name"].lower(),
            )).pk

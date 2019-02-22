from django import forms

from concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period, Topic
from ddionrails.helpers import lower_dict_names


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = Topic.DOR.io_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)
        if "name" not in self.data.keys():
            self.data["name"] = self.data.get("topic_name")


class ConceptForm(forms.ModelForm):
    class Meta:
        model = Concept
        fields = ("name", "label", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)

        if "name" not in self.data.keys():
            self.data["name"] = self.data.get("concept_name")


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ("study", "name", "label", "description", "definition")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)
        if "name" not in self.data.keys():
            self.data["name"] = self.data.get("period_name")


class AnalysisUnitForm(forms.ModelForm):
    class Meta:
        model = AnalysisUnit
        fields = ("name", "label", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)
        if "name" not in self.data.keys():
            self.data["name"] = self.data.get("analysis_unit_name")


class ConceptualDatasetForm(forms.ModelForm):
    class Meta:
        model = ConceptualDataset
        fields = ("name", "label", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_dict_names(self.data)
        if "name" not in self.data.keys():
            self.data["name"] = self.data.get("conceptual_dataset_name")

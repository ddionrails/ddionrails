import logging

from django import forms

from studies.models import Study

from .models import Instrument, Question

logger = logging.getLogger("imports")


class InstrumentForm(forms.ModelForm):

    class Meta:
        model = Instrument
        fields = ["name", "label", "description", "study"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["name"] = self.data["instrument_name"].lower()
        if "study" not in self.data.keys():
            self.data["study"] = Study.objects.get(
                name=self.data.get("study_name")
            ).pk


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ["instrument", "name", "label", "description", "image_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["name"] = self.data["question_name"].lower()
        self._set_instrument()

    def _set_instrument(self):
        if "instrument" in self.data.keys():
            self.data["instrument_object"] = Instrument.objects.get(
                pk=self.data["instrument"]
            )
        else:
            study = Study.objects.get(
                name=self.data.get("study_name")
            )
            self.data["instrument_object"] = Instrument.objects.get(
                study=study,
                name=self.data.get("instrument_name"),
            )
            self.data["instrument"] = self.data["instrument_object"].pk

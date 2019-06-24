# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" ModelForms for ddionrails.studies app """

from django import forms

from .models import Study


class StudyInitialForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["name", "repo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data["name"] = self.data["name"].lower()


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["name", "label", "description"]

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for forms in ddionrails.data app"""

from uuid import UUID

from django.test import TestCase

from ddionrails.data.forms import DatasetForm, VariableForm
from ddionrails.studies.models import Study
from tests.model_factories import FAKE, StudyFactory


class TestDatasetForm(TestCase):

    study: Study
    valid_dataset_data: dict[str, UUID | str]

    @classmethod
    def setUpClass(cls) -> None:
        cls.study = StudyFactory()
        cls.valid_dataset_data = {"study": cls.study.id, "dataset_name": FAKE.word()}
        return super().setUpClass()

    def test_form_with_valid_data(self):
        form = DatasetForm(data=self.valid_dataset_data)
        assert form.is_valid() is True
        dataset = form.save()
        assert dataset.name == self.valid_dataset_data["dataset_name"]

    def test_form_with_valid_data_uppercase(self):
        self.valid_dataset_data["dataset_name"] = "SOME-DATASET"
        form = DatasetForm(data=self.valid_dataset_data)
        assert form.is_valid() is True
        dataset = form.save()
        assert dataset.name == "SOME-DATASET"


class TestVariableForm(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.study = StudyFactory()
        cls.valid_variable_data = {
            "variable_name": "some-variable",
            "dataset_name": "some-dataset",
            "study_object": cls.study,
        }
        return super().setUpClass()

    def test_form_with_invalid_data(self):
        invalid_variable_data = {
            "variable_name": "",
            "dataset_name": "",
            "study_object": self.study,
        }
        form = VariableForm(data=invalid_variable_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self):
        form = VariableForm(data=self.valid_variable_data)
        assert form.is_valid() is True
        variable = form.save()
        assert variable.name == self.valid_variable_data["variable_name"]
        assert variable.dataset.name == self.valid_variable_data["dataset_name"]

    def test_form_with_valid_data_with_concept(self):
        self.valid_variable_data["concept_name"] = "some-concept"
        form = VariableForm(data=self.valid_variable_data)
        assert form.is_valid() is True
        variable = form.save()
        assert variable.name == self.valid_variable_data["variable_name"]
        assert variable.dataset.name == self.valid_variable_data["dataset_name"]

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for forms in ddionrails.data app """

from uuid import UUID

import pytest
from django.test import LiveServerTestCase

from ddionrails.data.forms import DatasetForm, VariableForm
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.data, pytest.mark.forms]  # pylint: disable=invalid-name


@pytest.mark.usefixtures("study")
class TestDatasetForm(LiveServerTestCase):

    study: Study
    valid_dataset_data: dict[str, UUID | str]

    def setUp(self) -> None:
        self.valid_dataset_data = {"study": self.study.id, "dataset_name": "some-dataset"}
        return super().setUp()

    def test_form_with_valid_data(self):
        form = DatasetForm(data=self.valid_dataset_data)
        assert form.is_valid() is True
        dataset = form.save()
        assert dataset.name == self.valid_dataset_data["dataset_name"]

    @pytest.mark.django_db
    def test_form_with_valid_data_uppercase(self):
        self.valid_dataset_data["dataset_name"] = "SOME-DATASET"
        form = DatasetForm(data=self.valid_dataset_data)
        assert form.is_valid() is True
        dataset = form.save()
        assert dataset.name == "SOME-DATASET"


class TestVariableForm:
    def test_form_with_invalid_data(self, invalid_variable_data):
        form = VariableForm(data=invalid_variable_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, valid_variable_data):
        form = VariableForm(data=valid_variable_data)
        assert form.is_valid() is True
        variable = form.save()
        assert variable.name == valid_variable_data["variable_name"]
        assert variable.dataset.name == valid_variable_data["dataset_name"]

    def test_form_with_valid_data_with_concept(
        self, valid_variable_data
    ):  # pylint: disable=invalid-name
        valid_variable_data["concept_name"] = "some-concept"
        form = VariableForm(data=valid_variable_data)
        assert form.is_valid() is True
        variable = form.save()
        assert variable.name == valid_variable_data["variable_name"]
        assert variable.dataset.name == valid_variable_data["dataset_name"]

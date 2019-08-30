# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for forms in ddionrails.data app """

import pytest
from django.core.exceptions import ValidationError

from ddionrails.data.forms import VariableForm

pytestmark = [pytest.mark.data, pytest.mark.forms]  # pylint: disable=invalid-name


class TestVariableForm:
    def test_form_with_invalid_data(self, invalid_variable_data):
        with pytest.raises(ValidationError):
            VariableForm(data=invalid_variable_data)

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

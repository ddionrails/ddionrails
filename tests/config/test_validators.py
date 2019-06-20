# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for validators in ddionrails.config app """

import pytest
from django.core.exceptions import ValidationError

from config.validators import validate_lowercase


class TestValidators:
    def test_validate_lowercase_with_valid_value(self):
        value = "test"
        validate_lowercase(value)
        assert value == value.lower()

    def test_validate_lowercase_with_invalid_value(self):
        value = "TEST"
        with pytest.raises(ValidationError) as excinfo:
            validate_lowercase(value)
            assert "is not lower case" in excinfo.value

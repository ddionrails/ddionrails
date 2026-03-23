# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for validators in ddionrails.config app"""

from unittest import TestCase

from django.core.exceptions import ValidationError

from config.validators import validate_lowercase


class TestValidators(TestCase):

    def test_validate_lowercase_with_valid_value(self):
        value = "test"
        validate_lowercase(value)
        self.assertEqual(value, value.lower())

    def test_validate_lowercase_with_invalid_value(self):
        value = "TEST"
        with self.assertRaises(ValidationError) as excinfo:
            validate_lowercase(value)
            self.assertIn("is not lower case", getattr(excinfo, "value"))

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for helpers in ddionrails.imports app"""

from unittest.mock import patch

from django.test import TestCase

from ddionrails.imports.helpers import read_csv


class TestHelpers(TestCase):

    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv_file = read_csv(filename, path)
        self.assertIn("study_name", csv_file[0].keys())

    def test_read_csv_without_path(self):
        with patch("builtins.open") as mocked_open:
            with patch("csv.DictReader") as mocked_csv_dict_reader:
                return_value = [dict(study_name="soep-core", dataset_name="abroad")]
                mocked_csv_dict_reader.return_value = return_value
                filename = "sample.csv"
                content = read_csv(filename)
                mocked_open.assert_called_once_with(filename, "r", encoding="utf8")
                mocked_csv_dict_reader.assert_called_once()
                self.assertIn("study_name", content[0].keys())

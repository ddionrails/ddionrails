# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.imports app """

import unittest

import pytest
import tablib

from ddionrails.imports.helpers import (
    add_concept_id_to_dataset,
    hash_with_base_uuid,
    read_csv,
    rename_dataset_headers,
)


@pytest.mark.usefixtures("tablib_dataset", "unittest_mock")
class TestHelpers(unittest.TestCase):
    dataset = tablib.Dataset()

    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv = read_csv(filename, path)
        print(csv)
        assert "study_name" in csv[0].keys()

    def test_read_csv_without_path(self):
        mocked_open = self.mocker.patch("builtins.open")
        mocked_csv_dict_reader = self.mocker.patch("csv.DictReader")
        return_value = [dict(study_name="soep-core", dataset_name="abroad")]
        mocked_csv_dict_reader.return_value = return_value
        filename = "sample.csv"
        content = read_csv(filename)
        mocked_open.assert_called_once_with(filename, "r")
        mocked_csv_dict_reader.assert_called_once()
        assert "study_name" in content[0].keys()

    def test_add_concept_id_to_dataset(self):
        old_column_length = len(self.dataset.headers)
        expected = hash_with_base_uuid(name=f'concept:{self.dataset["name"][0]}')

        add_concept_id_to_dataset(dataset=self.dataset, column_name="name")

        new_column_length = len(self.dataset.headers)
        # Do we have a new column?
        self.assertLess(old_column_length, new_column_length)

        # Do we have expected column name and value for the id?
        result = self.dataset["name_id"][0]
        self.assertEqual(expected, result)

    def test_rename_dataset_headers(self):
        rename_mapping = {"label": "new_label"}
        rename_dataset_headers(self.dataset, rename_mapping)
        expected = ["name", "new_label"]
        self.assertEqual(expected, self.dataset.headers)


@pytest.fixture
def tablib_dataset(request):
    headers = ("name", "label")
    name = "some-concept"
    label = "Some concept"
    values = (name, label)
    dataset = tablib.Dataset(values, headers=headers)

    if request.instance:
        request.instance.dataset = dataset
    else:
        return dataset
    return None


@pytest.fixture
def unittest_mock(request, mocker):
    request.instance.mocker = mocker

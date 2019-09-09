# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.imports app """

import unittest
from typing import Callable

import pytest
import requests_mock
import tablib
from pytest_mock import MockFixture

from ddionrails.imports.helpers import (
    add_concept_id_to_dataset,
    download_image,
    hash_with_base_uuid,
    read_csv,
    rename_dataset_headers,
)


@pytest.mark.usefixtures("tablib_dataset", "unittest_mock")
class TestHelpers(unittest.TestCase):
    dataset = tablib.Dataset()
    mocker = MockFixture

    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv = read_csv(filename, path)
        print(csv)
        assert "study_name" in csv[0].keys()

    def test_read_csv_without_path(self):
        mocked_open = self.mocker.patch("builtins.open")  # pylint: disable=no-member
        mocked_csv_dict_reader = self.mocker.patch(  # pylint: disable=no-member
            "csv.DictReader"
        )
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

    def test_download_image(self):
        self.assertIsInstance(download_image, Callable)
        _url = "http://test.de"
        expected = b"data"
        with requests_mock.mock() as mocked_request:
            mocked_request.get(_url, content=expected)
            result = download_image(_url).getvalue()
        self.assertEqual(expected, result)

    def test_rename_dataset_headers(self):
        rename_mapping = {"label": "new_label"}
        rename_dataset_headers(self.dataset, rename_mapping)
        expected = ["name", "new_label"]
        self.assertEqual(expected, self.dataset.headers)


@pytest.fixture(name="tablib_dataset")
def _tablib_dataset(request):
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


@pytest.fixture(name="unittest_mock")
def _unittest_mock(request, mocker):
    request.instance.mocker = mocker

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.imports app """

import pytest
import tablib

from ddionrails.imports.helpers import read_csv, rename_dataset_headers


class TestHelpers:
    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv = read_csv(filename, path)
        print(csv)
        assert "study_name" in csv[0].keys()

    def test_read_csv_without_path(self, mocker):
        mocked_open = mocker.patch("builtins.open")
        mocked_csv_dict_reader = mocker.patch("csv.DictReader")
        return_value = [dict(study_name="soep-core", dataset_name="abroad")]
        mocked_csv_dict_reader.return_value = return_value
        filename = "sample.csv"
        content = read_csv(filename)
        mocked_open.assert_called_once_with(filename, "r")
        mocked_csv_dict_reader.assert_called_once()
        assert "study_name" in content[0].keys()


@pytest.fixture
def tablib_dataset():
    headers = ("name", "label")
    name = "some-concept"
    label = "Some concept"
    values = (name, label)
    return tablib.Dataset(values, headers=headers)


def test_rename_dataset_headers(tablib_dataset):
    rename_mapping = {"label": "new_label"}
    rename_dataset_headers(tablib_dataset, rename_mapping)
    expected = ["name", "new_label"]
    assert expected == tablib_dataset.headers

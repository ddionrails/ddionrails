# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for helpers in ddionrails.imports app """

import unittest
from io import BytesIO

import pytest
import requests_mock
import tablib
from filer.models import Folder, Image
from pytest_mock import MockFixture

from ddionrails.imports.helpers import (
    add_concept_id_to_dataset,
    add_image_to_dataset,
    download_image,
    hash_with_base_uuid,
    read_csv,
    rename_dataset_headers,
    store_image,
)


@pytest.mark.django_db
@pytest.mark.usefixtures(
    "tablib_dataset", "unittest_mock", "variable_image_file", "question_image_dataset"
)
class TestHelpers(unittest.TestCase):
    dataset = tablib.Dataset()
    question_image_dataset = tablib.Dataset()
    mocker = MockFixture
    # This is overwritten by a fixture function
    variable_image_file = lambda file_type, size=1: BytesIO()

    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv = read_csv(filename, path)
        self.assertIn("study_name", csv[0].keys())

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
        self.assertIn("study_name", content[0].keys())

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
        """ Can we get a file from a web address? """
        url = "http://test.de"
        expected = self.variable_image_file("png").getvalue()
        with requests_mock.mock() as mocked_request:
            mocked_request.get(url, content=expected)
            result = download_image(url).getvalue()
        self.assertEqual(expected, result)

    def test_add_image_id_to_dataset(self):
        """ Can we get the id of a loaded and saved image?

        add_image_to_dataset should:
            * Save an image, located at a web address, into the database as FilerImage.
            * Add its id to the tablib.Dataset give to it as argument.
        """
        expected_image_bytes = {
            "en": self.variable_image_file("png", size=10).getvalue(),
            # Filer will check if an image already exists.
            # in order to test if the import for english and german images
            # worked the images have to be different, so this one gets a different size.
            "de": self.variable_image_file("jpeg", size=11).getvalue(),
        }
        url = {
            "en": self.question_image_dataset["url"][0],
            "de": self.question_image_dataset["url_de"][0],
        }
        label = {
            "en": self.question_image_dataset["label"][0],
            "de": self.question_image_dataset["label_de"][0],
        }
        expected_columns = [
            "question_id",
            "question_image_id",
            "image",
            "label",
            "language",
        ]

        with requests_mock.mock() as mocked_request:
            mocked_request.get(url["en"], content=expected_image_bytes["en"])
            mocked_request.get(url["de"], content=expected_image_bytes["de"])
            add_image_to_dataset(self.question_image_dataset)

        result = self.question_image_dataset

        for expected_column in expected_columns:
            self.assertIn(expected_column, result.headers)

        for language in ("en", "de"):
            # Is the language column filled correctly?
            self.assertIn(language, result["language"])
            # Is the label, that is inside the same row as the current language,
            # the correct value for that language? I.e. is the english label in
            # the english row and the german label in the german row?
            language_row = result["language"].index(language)
            self.assertEqual(label[language], result["label"][language_row])
            _image_id = result["image"][language_row].pk
            image = Image.objects.get(pk=_image_id)
            image_bytes = image.file.open().read()
            self.assertEqual(expected_image_bytes[language], image_bytes)

    def test_rename_dataset_headers(self):
        rename_mapping = {"label": "new_label"}
        rename_dataset_headers(self.dataset, rename_mapping)
        expected = ["name", "new_label"]
        self.assertEqual(expected, self.dataset.headers)

    def test_store_image(self):
        """ Can the QuestionImage store an image file? """
        image_file = self.variable_image_file(file_type="png", size=1)
        image_info = {
            "name": "test_image",
            "folders": {"child": "test", "parent": "images"},
        }
        image_info["name"] = "test_image"
        test_folder = "{parent}/{child}/".format(**image_info["folders"])

        _, image_key = store_image(image_file, path=test_folder, name=image_info["name"])

        # Has the propper folder structure been created?
        parent, parent_created = Folder.objects.get_or_create(
            name=image_info["folders"]["parent"]
        )
        self.assertFalse(parent_created)
        _, child_created = Folder.objects.get_or_create(
            parent=parent, name=image_info["folders"]["child"]
        )
        self.assertFalse(child_created)

        # Is the Image inside the database?
        result_image, created = Image.objects.get_or_create(pk=image_key)
        self.assertFalse(created)
        result_image_bytes = result_image.file.open().read()
        self.assertEqual(image_file.getvalue(), result_image_bytes)
        self.assertEqual(image_info["name"], result_image.name)


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

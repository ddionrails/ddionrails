# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for helpers in ddionrails.imports app """

import unittest
from io import BytesIO

import pytest
import requests_mock
from filer.models import Folder, Image
from pytest_mock import MockFixture

from ddionrails.imports.helpers import download_image, read_csv, store_image


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_mock", "variable_image_file")
class TestHelpers(unittest.TestCase):
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

    def test_download_image(self):
        """ Can we get a file from a web address? """
        url = "http://test.de"
        expected = self.variable_image_file("png").getvalue()
        with requests_mock.mock() as mocked_request:
            mocked_request.get(url, content=expected)
            result = download_image(url).getvalue()
        self.assertEqual(expected, result)

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


@pytest.fixture(name="unittest_mock")
def _unittest_mock(request, mocker):
    request.instance.mocker = mocker

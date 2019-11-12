# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for helpers in ddionrails.imports app """

import csv
import glob
import unittest
from io import StringIO
from random import choices
from typing import Callable, Dict, List, Optional, Tuple, TypedDict
from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from filer.models import Folder, Image
from pytest_mock import MockFixture

from ddionrails.imports.helpers import (
    download_image,
    patch_instruments,
    read_csv,
    store_image,
)
from ddionrails.imports.types import QuestionsImages
from tests.conftest import MockOpener, VariableImageFile


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_mock", "variable_image_file")
class TestHelpers(unittest.TestCase):
    mocker: MockFixture
    # This is overwritten by a fixture function
    variable_image_file: VariableImageFile

    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv_file = read_csv(filename, path)
        self.assertIn("study_name", csv_file[0].keys())

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

    def test_download_image_too_large(self):
        """ The download function should load anything above 200KB. """
        url = "http://test.de"
        # This is one byte too large.
        image = b"A" * 200001
        with requests_mock.mock() as mocked_request:
            mocked_request.get(url, content=image)
            result = download_image(url)
        self.assertEqual(None, result)

    def test_store_image(self):
        """ Can the QuestionImage store an image file? """
        image_file = self.variable_image_file(file_type="png", size=1)

        class ImageTestInfo(TypedDict):
            name: str
            folders: Dict[str, str]

        image_info: ImageTestInfo = {
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


@pytest.mark.usefixtures("questions_images_csv")
class TestTemporaryHelper(unittest.TestCase):

    questions_images_csv: str
    questions_images: List[QuestionsImages]

    def setUp(self):
        self.csv_path = "/test/metadata"
        self.json_path = "/test/ddionrails/instruments"
        self.csv_file = f"{self.csv_path}/questions_images.csv"
        self.json_file = f"{self.json_path}/test_instruments.json"

        return super().setUp()

    @patch("glob.glob", new_callable=MagicMock, spec=glob)
    @patch("builtins.open", new_callable=MockOpener)
    def test_patch_instruments(self, mocked_open, mocked_glob):

        mocked_glob.return_value = [self.json_file]
        mocked_open.register_file(self.csv_file, self.questions_images_csv)
        mocked_open.register_file(f"{self.json_path}/test_instrument.json", "json")

        patch_instruments(repository_dir="/test", instruments_dir=self.json_path)

        self.assertIn(self.csv_file, mocked_open.call_history)
        mocked_glob.assert_called_with(f"{self.json_path}/*")


@pytest.fixture(name="unittest_mock")
def _unittest_mock(request, mocker):
    request.instance.mocker = mocker


@pytest.fixture(name="questions_images_csv")
def _question_images_csv(
    request, questions_images_data_factory
) -> Optional[Tuple[str, List[QuestionsImages]]]:
    table: List[QuestionsImages] = [questions_images_data_factory() for _ in range(1, 10)]
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=table[0].keys())
    writer.writeheader()
    for row in table:
        writer.writerow(row)
    if request.instance:
        request.instance.questions_images_csv = str(csv_file.getvalue())
        request.instance.questions_images = table
    else:
        return (str(csv_file.getvalue()), table)
    return None


@pytest.fixture(name="questions_images_data_factory")
def _questions_images_data_factory() -> Callable[[], QuestionsImages]:
    class Factory:
        """Build content that fits into a QuestionsImages object.

        Can be used write rows to a questions_images.csv, using the csv.DictWriter.
        Study and Instrument name remain consistent in an Instance while all other
        fields change with each call.
        Content is created with random characters from a large part of unicode characters.
        """

        _characters: List[str] = [chr(number) for number in range(1, 2047)]
        _content: QuestionsImages
        _constant_pairs: Dict[str, str]

        def __init__(self):
            self._constant_pairs = {
                "study": "".join(choices(self._characters, k=10)),
                "instrument": "".join(choices(self._characters, k=10)),
            }
            self._variable_headers = ("question", "url", "url_de", "label", "label_de")
            self._content = QuestionsImages

        def __call__(self):
            content: Dict[str] = dict()
            content.update(dict(self._constant_pairs))
            for field in self._variable_headers:
                content[field] = "".join(choices(self._characters, k=10))
            self._content = content
            return content

        @property
        def content(self):
            return self.content.copy()

    return Factory()

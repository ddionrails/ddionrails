# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for helpers in ddionrails.imports app """

import csv
import unittest
from io import StringIO
from random import choices
from typing import Callable, Dict, List, Optional, Tuple

import pytest
from pytest_mock import MockerFixture

from ddionrails.imports.helpers import read_csv
from ddionrails.imports.types import QuestionsImages
from tests.conftest import VariableImageFile


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_mock", "variable_image_file")
class TestHelpers(unittest.TestCase):
    mocker: MockerFixture
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
        mocked_open.assert_called_once_with(filename, "r", encoding="utf8")
        mocked_csv_dict_reader.assert_called_once()
        self.assertIn("study_name", content[0].keys())


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
            content: Dict[str, str] = {}
            content.update(dict(self._constant_pairs))
            for field in self._variable_headers:
                content[field] = "".join(choices(self._characters, k=10))
            self._content = content
            return content

        @property
        def content(self):
            return self.content.copy()

    return Factory()

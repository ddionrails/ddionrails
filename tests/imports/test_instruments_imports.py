"""Test imports from the instruments app."""
import unittest
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Generator

import pytest

from ddionrails.instruments.imports import question_import_direct
from ddionrails.instruments.models import Instrument, Question

TEST_FILES = Path("./tests/imports/test_data/").absolute()


@pytest.fixture(scope="class", name="tmp_dir")
def _tmp_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    with TemporaryDirectory() as directory:
        setattr(request.cls, "data_dir", Path(directory).absolute())
        copytree(TEST_FILES, directory, dirs_exist_ok=True)
        yield


@pytest.mark.django_db
@pytest.mark.usefixtures("tmp_dir", "instrument")
class QuestionImport(unittest.TestCase):
    """Test all imports associated with the questions.csv.

    This includes import of Question and QuestionItem objects.
    """

    data_dir: Path
    instrument: Instrument

    def setUp(self) -> None:
        self.instrument: Instrument = Instrument.objects.get(name="some-instrument")
        question_exists = len(
            list(Question.objects.filter(name="1", instrument=self.instrument))
        )
        self.assertEqual(0, question_exists)

    def test_main_question_import(self) -> None:
        """Test import of first question, that holds the items together."""

        question_import_direct(
            file=self.data_dir.joinpath("questions.csv"), study=self.instrument.study
        )
        question_name = "1"
        question, created = Question.objects.get_or_create(
            name=question_name, instrument=self.instrument
        )
        self.assertFalse(created, msg=f"Question {question_name} was not created.")

        expected_fields = {
            "name": "1",
            "label": "Please state the first name, sex, and date of birth:",
            "label_de": "Bitte geben Sie den Vornamen, Geburtsdatum und Geschlecht an:",
            "description": "",
            "description_de": "",
            "instruction": "",
            "instruction_de": "",
        }

        for field, value in expected_fields.items():
            self.assertEqual(value, getattr(question, field))

    def test_question_item_import(self) -> None:
        """Test import of first question, that holds the items together."""

        question_import_direct(
            file=self.data_dir.joinpath("questions.csv"), study=self.instrument.study
        )
        question_name = "1"
        question, _ = Question.objects.get_or_create(
            name=question_name, instrument=self.instrument
        )
        number_of_question_items = len(list(question.question_items.all()))
        self.assertEqual(8, number_of_question_items)

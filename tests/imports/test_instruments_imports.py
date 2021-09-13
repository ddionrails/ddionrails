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
        _, created = Question.objects.get_or_create(
            name=question_name, instrument=self.instrument
        )
        self.assertFalse(created, msg=f"Question {question_name} was not created.")

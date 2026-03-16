"""Test imports from the instruments app."""

from pathlib import Path
from shutil import copytree, rmtree

from django.test import TestCase

from ddionrails.instruments.imports.question_import import (
    answer_import,
    answer_relation_import,
    question_import,
)
from ddionrails.instruments.models import Answer, Instrument, Question
from tests.file_factories import tmp_import_path
from tests.model_factories import InstrumentFactory

TEST_FILES = Path("./tests/imports/test_data/").absolute()


class QuestionImport(TestCase):
    """Test all imports associated with the questions.csv.

    This includes import of Question and QuestionItem objects.
    """

    data_dir: Path
    instrument: Instrument

    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir, cls.patch_arguments = tmp_import_path()
        copytree(TEST_FILES, cls.data_dir, dirs_exist_ok=True)
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        rmtree(cls.data_dir)
        return super().tearDownClass()

    def setUp(self) -> None:
        self.instrument: Instrument = InstrumentFactory(
            name="some-instrument", study__name="test-study"
        )
        question_exists = len(
            list(Question.objects.filter(name="1", instrument=self.instrument))
        )
        self.assertEqual(0, question_exists)

    def test_main_question_import(self) -> None:
        """Test import of first question, that holds the items together."""

        question_import(
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

        question_import(
            file=self.data_dir.joinpath("questions.csv"), study=self.instrument.study
        )
        question_name = "1"
        question = Question.objects.get(name=question_name, instrument=self.instrument)
        question_items = list(question.question_items.all().order_by("position"))
        number_of_question_items = len(question_items)
        self.assertEqual(8, number_of_question_items)

        expected_fields_first_item = {
            "name": "1",
            "label": "Please state the first name, sex, and date of birth:",
            "label_de": "Bitte geben Sie den Vornamen, Geburtsdatum und Geschlecht an:",
            "description": "",
            "description_de": "",
            "instruction": "",
            "instruction_de": "",
            "scale": "txt",
            "input_filter": "test_filter",
            "goto": "",
            "position": 0,
        }
        expected_fields_last_item = {
            "name": "vsex",
            "label": "[de] (Geschlecht)",
            "label_de": "(Geschlecht)",
            "description": "",
            "description_de": "",
            "instruction": "",
            "instruction_de": "",
            "scale": "cat",
            "input_filter": "",
            "goto": "test_goto",
            "position": 7,
        }

        for field, value in expected_fields_first_item.items():
            self.assertEqual(value, getattr(question_items[0], field))

        for field, value in expected_fields_last_item.items():
            self.assertEqual(value, getattr(question_items[7], field))

    def test_answer_import(self) -> None:
        """Test the import and linking of answers to question items."""
        question_import(
            file=self.data_dir.joinpath("questions.csv"), study=self.instrument.study
        )
        answer_import(
            file=self.data_dir.joinpath("answers.csv"), study=self.instrument.study
        )
        answer_relation_import(
            file=self.data_dir.joinpath("answers.csv"), study=self.instrument.study
        )
        question_name = "1"
        question = Question.objects.get(name=question_name, instrument=self.instrument)
        question_items = list(question.question_items.all().order_by("position"))
        first_cat_item = question_items[7]

        self.assertEqual("cat", first_cat_item.scale)

        first_answers: Answer = first_cat_item.answers.all().order_by("value")
        self.assertEqual(1, first_answers[0].value)
        self.assertEqual(2, first_answers[1].value)

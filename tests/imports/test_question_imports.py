"""Test imports from the instruments app."""

from pathlib import Path
from shutil import copytree, rmtree
from unittest.mock import patch

from django.test import TestCase

from ddionrails.instruments.imports.question_import import (
    answer_import,
    answer_relation_import,
    question_import,
)
from ddionrails.instruments.models import Answer, Instrument, Question
from ddionrails.instruments.models.question_item import QuestionItem
from ddionrails.studies.models import Study
from tests.file_factories import destroy_tmp_path, import_data_factory, tmp_import_path
from tests.model_factories import InstrumentFactory, PeriodFactory, StudyFactory

TEST_FILES = Path("./tests/imports/test_data/").absolute()


class QuestionImport(TestCase):
    """Test all imports associated with the questions.csv.

    This includes import of Question and QuestionItem objects.
    """

    def setUp(self) -> None:
        self.tmp_path, self.patch_dict, self.files, self.file_content, self.study_name = (
            import_data_factory(clean_database=False)
        )
        self.path_path = patch(**self.patch_dict)
        self.path_path.start()
        self.study = Study.objects.get(name=self.study_name)

    def tearDown(self) -> None:
        self.path_path.stop()
        destroy_tmp_path(self.tmp_path)

    def test_main_question_import(self) -> None:
        """Test import of first question, that holds the items together."""
        Question.objects.all().delete()
        self.assertEqual(0, Question.objects.count())

        question_import(file=self.tmp_path.joinpath("questions.csv"), study=self.study)
        expected_fields = self.file_content["questions.csv"][0]
        question_name = expected_fields["name"]
        instrument_name = expected_fields["instrument"]
        question, created = Question.objects.get_or_create(
            name=question_name, instrument__name=instrument_name
        )
        self.assertFalse(created, msg=f"Question {question_name} was not created.")

        for field in ["name", "description", "description_de"]:
            self.assertEqual(expected_fields[field], getattr(question, field))

    def test_question_item_import(self) -> None:
        """Test import of first question, that holds the items together."""
        Question.objects.all().delete()
        self.assertEqual(0, Question.objects.count())

        question_import(file=self.tmp_path.joinpath("questions.csv"), study=self.study)
        for expected_fields in self.file_content["questions.csv"]:
            question_name = expected_fields["name"]
            instrument_name = expected_fields["instrument"]
            item, created = QuestionItem.objects.get_or_create(
                name=expected_fields["item"],
                question__instrument__name=instrument_name,
                question__name=question_name,
            )
            self.assertFalse(created, msg=f"Question {question_name} was not created.")

            self.assertEqual(expected_fields["text"], item.label)
            self.assertEqual(expected_fields["text_de"], item.label_de)

    def test_answer_import(self) -> None:
        """Test the import and linking of answers to question items."""
        Question.objects.all().delete()
        Answer.objects.all().delete()
        self.assertEqual(0, Question.objects.count())
        self.assertEqual(0, Answer.objects.count())

        question_import(file=self.tmp_path.joinpath("questions.csv"), study=self.study)
        answer_import(file=self.tmp_path.joinpath("answers.csv"), study=self.study)
        answer_relation_import(
            file=self.tmp_path.joinpath("answers.csv"), study=self.study
        )

        for answer in self.file_content["answers.csv"]:
            self.assertGreater(
                Answer.objects.filter(
                    label=answer["label"], label_de=answer["label_de"]
                ).count(),
                0,
                msg=f"{answer} was not imported",
            )

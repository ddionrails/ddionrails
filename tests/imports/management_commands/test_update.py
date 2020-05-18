# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import csv
import unittest
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from django.core.management import call_command

from ddionrails.concepts.models import Period
from ddionrails.data.models import Dataset, Variable
from ddionrails.imports.management.commands import update
from ddionrails.imports.manager import StudyImportManager
from ddionrails.workspace.models import Basket
from tests.data.factories import DatasetFactory
from tests.workspace.factories import BasketFactory

pytestmark = [pytest.mark.django_db]


IMPORT_PATH = Path("tests/functional/test_data/some-study/ddionrails/").absolute()

TEST_CASE = unittest.TestCase()


@pytest.fixture(name="mocked_update_single_study")
def _mocked_update_single_study(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_single_study"
    )


@pytest.fixture(name="mocked_update_study_partial")
def _mocked_update_study_partial(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_study_partial"
    )


@pytest.fixture(name="mocked_update_all_studies_completely")
def _mocked_update_all_studies_completely(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_all_studies_completely"
    )


@pytest.fixture(name="mocked_import_single_entity")
def _mocked_import_single_entity(mocker):
    return mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.import_single_entity"
    )


@pytest.fixture(name="mocked_import_all_entities")
def _mocked_import_all_entities(mocker):
    return mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.import_all_entities"
    )


def test_update_study_partial(study, mocked_import_single_entity):
    manager = StudyImportManager(study)
    entity = ("periods",)
    update.update_study_partial(manager, entity)
    mocked_import_single_entity.assert_called_once_with(entity[0])


@pytest.mark.django_db
@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study(study, mocker):
    with open(IMPORT_PATH.joinpath("variables.csv")) as variables_file:
        expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
    mocked_update_repo = mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.update_repo"
    )
    update.update_single_study(study, False, (), None)
    mocked_update_repo.assert_called_once()
    result = {variable.name for variable in Variable.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_variables, result)


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_local(study):
    local = True
    with open(IMPORT_PATH.joinpath("variables.csv")) as variables_file:
        expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
    update.update_single_study(study, local, (), None)
    result = {variable.name for variable in Variable.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_variables, result)


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_entity(study):

    entities = ("periods",)

    local = True
    with open(IMPORT_PATH.joinpath("periods.csv")) as periods_file:
        expected_periods = {row["name"] for row in csv.DictReader(periods_file)}
    update.update_single_study(study, local, entities, None)
    result = {period.name for period in Period.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_periods, result)


def test_update_single_study_entity_filename(study, mocked_import_single_entity):
    filename = "tests/imports/test_data/sample.csv"
    update.update_single_study(study, True, ("instruments",), filename)
    mocked_import_single_entity.assert_called_once_with("instruments", filename)


def test_update_all_studies_completely(
    study, mocked_update_single_study  # pylint: disable=unused-argument
):
    update.update_all_studies_completely(True)
    mocked_update_single_study.assert_called_once()


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_update_command_shows_help(option, capsys: CaptureFixture):
    """ Test "update" shows help """
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", option)

    TEST_CASE.assertEqual(0, error.exception.code)
    output = capsys.readouterr().out
    TEST_CASE.assertIn(
        "This command is used to update study metadata in ddionrails.", output
    )
    TEST_CASE.assertIn("--local", output)
    TEST_CASE.assertIn("--filename", output)


def test_update_command_without_study_name(mocked_update_all_studies_completely):
    """ Test "update" runs "update_all_studies_completely" when given no study name """
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update")

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_all_studies_completely.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_without_study_name_local(
    option, mocked_update_all_studies_completely
):
    """Test "update" runs "update_all_studies_completely" correctly with --local """
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", option)

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_all_studies_completely.assert_called_once_with(True, False)


def test_update_command_with_invalid_study_name(capsys: CaptureFixture):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", "study-not-in-db")

    TEST_CASE.assertEqual(1, error.exception.code)
    TEST_CASE.assertIn("does not exist", capsys.readouterr().err)


def test_update_command_with_valid_study_name(study, mocked_update_single_study):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name)

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_single_study.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_with_valid_study_name_local(
    study, option, mocked_update_single_study
):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, option)

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_single_study.assert_called_once_with(study, True, set(), None, False)


def test_update_command_with_valid_study_name_and_entity(
    study, mocked_update_single_study
):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "periods")

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_single_study.assert_called_once_with(
        study, False, {"periods"}, None, False
    )


def test_update_command_with_valid_study_name_and_invalid_entity(study):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "invalid-entity")

    TEST_CASE.assertEqual(1, error.exception.code)


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_valid_entity_and_filename(
    study, option, mocked_update_single_study
):
    filename = "tests/imports/test_data/sample.csv"
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "instruments", option, filename)

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_single_study.assert_called_once_with(
        study, False, {"instruments"}, Path(filename), False
    )


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_invalid_entity_and_filename(
    study, option, capsys: CaptureFixture
):
    filename = "tests/imports/test_data/sample.csv"

    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "periods", option, filename)

    TEST_CASE.assertEqual(1, error.exception.code)
    TEST_CASE.assertRegex(
        capsys.readouterr().err,
        ".*Support for single file import not available for entity.*",
    )


@pytest.mark.usefixtures(("mock_import_path"))
class TestUpdate(unittest.TestCase):
    def setUp(self):
        self.dataset = DatasetFactory(name="test-dataset")
        self.study = self.dataset.study
        basket = BasketFactory(name="test-basket")
        basket.study = self.study
        basket.save()
        self.basket_id = basket.id
        return super().setUp()

    def test_clean_update(self):
        """Does a clean update remove study data before the update?

        The clean import should remove all entities related to a study before
        the import of the study.
        There is no data provided to import for this test.
        After the clean import without data only the study object itself should
        remain in the database.
        The test dataset should be gone.
        """
        clean_import = True
        self.assertTrue(list(Dataset.objects.filter(id=self.dataset.id)))
        update.update_single_study(self.study, True, clean_import=clean_import)
        datasets_ids = [dataset.id for dataset in Dataset.objects.all()]
        self.assertNotIn(self.dataset.id, datasets_ids)
        self.assertTrue(bool(list(Basket.objects.filter(id=self.basket_id))))

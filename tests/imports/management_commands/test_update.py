# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import csv
import logging
import unittest
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command

from ddionrails.concepts.models import Period
from ddionrails.data.models import Dataset, Variable
from ddionrails.imports.management.commands import update
from ddionrails.imports.manager import StudyImportManager
from ddionrails.instruments.models import Instrument
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable
from tests.conftest import PatchImportPathArguments
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
    with open(IMPORT_PATH.joinpath("variables.csv"), encoding="utf8") as variables_file:
        expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
    mocked_update_repo = mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.update_repo"
    )
    manager = StudyImportManager(study, redis=False)
    update.update_single_study(study, False, (), "", manager=manager)
    mocked_update_repo.assert_called_once()
    result = {variable.name for variable in Variable.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_variables, result)


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_local(study):
    local = True
    with open(IMPORT_PATH.joinpath("variables.csv"), encoding="utf8") as variables_file:
        expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
    manager = StudyImportManager(study, redis=False)
    update.update_single_study(study, local, (), None, manager=manager)
    result = {variable.name for variable in Variable.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_variables, result)


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_entity(study):

    entities = ("periods",)

    local = True
    with open(IMPORT_PATH.joinpath("periods.csv"), encoding="utf8") as periods_file:
        expected_periods = {row["name"] for row in csv.DictReader(periods_file)}
    manager = StudyImportManager(study, redis=False)
    update.update_single_study(study, local, entities, None, manager=manager)
    result = {period.name for period in Period.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_periods, result)


def test_update_single_study_entity_filename(study, mocked_import_single_entity):
    filename = "tests/imports/test_data/sample.csv"
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "instruments.json", "-f", filename, "-l")
        TEST_CASE.assertEqual(0, error.exception.code)
    TEST_CASE.assertEqual(
        "instruments.json", mocked_import_single_entity.call_args.args[0]
    )
    TEST_CASE.assertEqual(Path(filename), mocked_import_single_entity.call_args.args[1])


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_entity_filename_without_redis(study):
    filename = Study().import_path().joinpath("instruments/some-instrument.json")
    with unittest.mock.patch("django_rq.enqueue") as redis_enqueue:
        with TEST_CASE.assertRaises(SystemExit) as error:
            call_command(
                "update", study.name, "instruments.json", "-f", filename, "-l", "-r"
            )
        TEST_CASE.assertEqual(0, error.exception.code)
        TEST_CASE.assertFalse(redis_enqueue.called)


@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study_entity_nonexistent_filename(study):
    filename = Study().import_path().joinpath("nonexistent-file.json")

    logger = logging.getLogger("ddionrails.imports.manager")
    with unittest.mock.patch.object(logger, "error") as log:
        with TEST_CASE.assertRaises(SystemExit) as error:
            call_command("update", study.name, "instruments.json", "-f", filename, "-l")
        logging.getLogger("ddionrails.imports.manager")
        TEST_CASE.assertEqual(1, error.exception.code)
        log.assert_called_once_with(
            'Study "%s" has no file: "%s"', "some-study", "nonexistent-file.json"
        )


def test_update_all_studies_completely(
    study, mocked_update_single_study  # pylint: disable=unused-argument
):
    update.update_all_studies_completely(True)
    mocked_update_single_study.assert_called_once()


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_update_command_shows_help(option, capsys: CaptureFixture):
    """Test "update" shows help"""
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
    """Test "update" runs "update_all_studies_completely" when given no study name"""
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update")

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_all_studies_completely.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_without_study_name_local(
    option, mocked_update_all_studies_completely
):
    """Test "update" runs "update_all_studies_completely" correctly with --local"""
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", option)

    TEST_CASE.assertEqual(0, error.exception.code)
    mocked_update_all_studies_completely.assert_called_once_with(True, False, redis=True)


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

    call_args = mocked_update_single_study.call_args.args
    call_kwargs = mocked_update_single_study.call_args.kwargs
    TEST_CASE.assertEqual((study, True, tuple(), None, False), call_args)
    TEST_CASE.assertEqual(
        (study, True), (call_kwargs["manager"].study, call_kwargs["manager"].redis)
    )


def test_update_command_with_valid_study_name_and_entity(
    study, mocked_update_single_study
):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, ("periods"))

    manager = StudyImportManager(study)
    TEST_CASE.assertEqual(0, error.exception.code)
    call_args = mocked_update_single_study.call_args.args
    call_kwargs = mocked_update_single_study.call_args.kwargs
    TEST_CASE.assertEqual((study, False, tuple(("periods",)), None, False), call_args)
    TEST_CASE.assertEqual(
        (manager.study, manager.redis),
        (call_kwargs["manager"].study, call_kwargs["manager"].redis),
    )


def test_update_command_with_valid_study_name_and_invalid_entity(study):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "invalid-entity")

    TEST_CASE.assertEqual(1, error.exception.code)


@pytest.mark.parametrize("option", ("-f", "--filename"))
@pytest.mark.usefixtures(("mock_import_path"))
def test_update_command_with_valid_study_name_and_valid_entity_and_filename(
    study, option
):
    file_path = Study().import_path().joinpath("instruments/some-instrument.json")

    with TEST_CASE.assertRaises(Instrument.DoesNotExist):
        Instrument.objects.get(name="some-instrument")

    with unittest.mock.patch("ddionrails.imports.manager.Repository") as git_api:
        with TEST_CASE.assertRaises(SystemExit) as error:
            call_command("update", study.name, "instruments.json", option, file_path)
            git_api: unittest.mock.MagicMock
            git_api.pull_or_clone.assert_called()
            git_api.set_commit_id.assert_called()

        TEST_CASE.assertEqual(0, error.exception.code)
        Instrument.objects.get(name="some-instrument")


@pytest.mark.usefixtures("mock_import_path", "period", "analysis_unit")
def test_instrument_import(study, period, analysis_unit):

    with TEST_CASE.assertRaises(Instrument.DoesNotExist):
        Instrument.objects.get(name="some-instrument")

    with unittest.mock.patch("ddionrails.imports.manager.Repository"):
        with TEST_CASE.assertRaises(SystemExit) as error:
            call_command("update", study.name, "instruments.json")
        TEST_CASE.assertEqual(0, error.exception.code)

        with TEST_CASE.assertRaises(SystemExit) as error:
            call_command("update", study.name, "instruments")

        TEST_CASE.assertEqual(0, error.exception.code)
        instrument = Instrument.objects.get(name="some-instrument")
        TEST_CASE.assertEqual("some-type", instrument.type["en"])
        TEST_CASE.assertEqual("ein-typ", instrument.type["de"])
        TEST_CASE.assertEqual("1", instrument.type["position"])
        TEST_CASE.assertEqual("some-mode", instrument.mode)
        TEST_CASE.assertEqual(period, instrument.period)
        TEST_CASE.assertEqual(analysis_unit, instrument.analysis_unit)


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

    patch_argument_dict: PatchImportPathArguments

    def setUp(self):
        self.dataset = DatasetFactory(name="test-dataset")
        self.study = self.dataset.study
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
        manager = StudyImportManager(self.study, redis=False)
        update.update_single_study(
            self.study, True, clean_import=clean_import, manager=manager
        )
        datasets_ids = [dataset.id for dataset in Dataset.objects.all()]
        self.assertNotIn(self.dataset.id, datasets_ids)

    def test_basket_protection(self):
        """A clean update should leaf baskets intact."""
        clean_import = False

        basket = BasketFactory(name="study_basket")

        manager = StudyImportManager(self.study, redis=False)
        update.update_single_study(
            self.study, True, clean_import=clean_import, manager=manager
        )
        variable = Variable.objects.get(name="some-variable")
        outdated_variable = Variable.objects.get(name="some-third-variable")

        basket_variable = BasketVariable(basket=basket, variable=variable)
        outdated_basket_variable = BasketVariable(
            basket=basket, variable=outdated_variable
        )
        outdated_basket_variable.save()
        basket.save()
        basket_variable.save()
        outdated_id = outdated_variable.id
        variable_id = variable.id
        basket_id = basket.id

        import_files = Path(self.patch_argument_dict["return_value"])
        new_variables = """study_name,dataset_name,name,concept_name,image_url
some-study,some-dataset,some-variable,some-concept,https://variable-image.de
some-study,some-dataset,some-other-variable,some-concept,https://variable-other-image.de
"""
        with open(import_files.joinpath("variables.csv"), "w", encoding="utf8") as file:
            file.write(new_variables)

        clean_import = True
        manager = StudyImportManager(self.study, redis=False)
        update.update_single_study(
            self.study, True, clean_import=clean_import, manager=manager
        )

        with self.assertRaises(ObjectDoesNotExist):
            Variable.objects.get(name="some-third-variable")

        variable = Variable.objects.get(name="some-variable")
        self.assertEqual(1, BasketVariable.objects.all().count())
        self.assertEqual(
            1, BasketVariable.objects.filter(variable_id=variable_id).count()
        )
        self.assertEqual(
            0, BasketVariable.objects.filter(variable_id=outdated_id).count()
        )
        self.assertEqual(1, Basket.objects.filter(id=basket_id).count())

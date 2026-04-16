# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for "update" management command for ddionrails project"""

import csv
import logging
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.test import TestCase

from ddionrails.concepts.models import Period
from ddionrails.data.models import Dataset, Variable
from ddionrails.imports.management.commands.update import (
    StudyImportManager,
    update,
    update_all_studies_completely,
    update_single_study,
    update_study_partial,
)
from ddionrails.instruments.models import Instrument
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable
from tests.conftest import PatchImportPathArguments
from tests.data.factories import DatasetFactory
from tests.model_factories import StudyFactory
from tests.workspace.factories import BasketFactory

pytestmark = [pytest.mark.django_db]


IMPORT_PATH = Path("tests/functional/test_data/some-study/ddionrails/").absolute()

TEST_CASE = unittest.TestCase()


def get_options(study_name):
    options = {}
    options["study_name"] = study_name
    options["entity"] = []
    options["local"] = True
    options["filename"] = None
    options["clean_import"] = False
    options["no_redis"] = True
    return options


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


@pytest.fixture(name="mocked_import_all_entities")
def _mocked_import_all_entities(mocker):
    return mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.import_all_entities"
    )


class TestUpdate_(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.mock_update_single = patch.object(StudyImportManager, "import_single_entity")

        self.mock_single_study = patch(
            "ddionrails.imports.management.commands.update.update_single_study"
        )
        self.single_entity_mocker = self.mock_update_single.start()
        self.single_study_mocker = self.mock_single_study.start()

    def test_update_study_partial(self):
        manager = StudyImportManager(self.study)
        entity = ("periods",)
        update_study_partial(manager, entity)
        self.single_entity_mocker.assert_called_once_with(entity[0])

    def test_update_all_studies_completely(self):
        update_all_studies_completely(True)
        self.single_study_mocker.assert_called_once()

    @patch(
        (
            "ddionrails.imports.management.commands."
            "update.StudyImportManager.import_single_entity"
        )
    )
    def test_update_single_study_entity_filename(self, mocked_import_single_entity):
        self.mock_single_study.stop()
        filename = "tests/imports/test_data/sample.csv"
        with self.assertRaises(SystemExit) as error:
            call_command(
                "update", self.study.name, "instruments.json", "-f", filename, "-l"
            )
            TEST_CASE.assertEqual(0, error.exception.code)
        TEST_CASE.assertEqual(
            "instruments.json", mocked_import_single_entity.call_args.args[0]
        )
        TEST_CASE.assertEqual(
            Path(filename), mocked_import_single_entity.call_args.args[1]
        )

    def tearDown(self) -> None:
        self.mock_update_single.stop()
        self.mock_single_study.stop()
        return super().tearDown()

    def test_update_command_with_valid_study_name(self):
        with self.assertRaises(SystemExit) as error:
            call_command("update", self.study.name)

        self.assertEqual(0, error.exception.code)
        self.single_study_mocker.assert_called_once()

    def test_update_command_with_valid_study_name_local(self):
        for option in ["-l", "--local"]:
            with TEST_CASE.assertRaises(SystemExit) as error:
                call_command("update", self.study.name, option)

            TEST_CASE.assertEqual(0, error.exception.code)

            call_args = self.single_study_mocker.call_args.args
            call_kwargs = self.single_study_mocker.call_args.kwargs
            self.assertEqual((self.study, True, tuple(), None, False), call_args)
            self.assertEqual(
                (self.study, True),
                (call_kwargs["manager"].study, call_kwargs["manager"].redis),
            )

    def test_update_command_with_valid_study_name_and_entity(self):
        with self.assertRaises(SystemExit) as error:
            call_command("update", self.study.name, ("periods"))

        manager = StudyImportManager(self.study)
        self.assertEqual(0, error.exception.code)
        call_args = self.single_study_mocker.call_args.args
        call_kwargs = self.single_study_mocker.call_args.kwargs
        self.assertEqual((self.study, False, tuple(("periods",)), None, False), call_args)
        self.assertEqual(
            (manager.study, manager.redis),
            (call_kwargs["manager"].study, call_kwargs["manager"].redis),
        )


@pytest.mark.django_db
@pytest.mark.usefixtures(("mock_import_path"))
def test_update_single_study(study, mocker):
    with open(IMPORT_PATH.joinpath("variables.csv"), encoding="utf8") as variables_file:
        expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
    mocked_update_repo = mocker.patch(
        "ddionrails.imports.management.commands.update.set_up_repo"
    )
    manager = StudyImportManager(study, redis=False)
    update_single_study(study, False, (), "", manager=manager)
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
    update_single_study(study, local, (), None, manager=manager)
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
    update_single_study(study, local, entities, None, manager=manager)
    result = {period.name for period in Period.objects.all()}
    TEST_CASE.assertNotEqual(0, len(result))
    TEST_CASE.assertEqual(expected_periods, result)


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


def test_update_command_with_valid_study_name_and_invalid_entity(study):
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "invalid-entity")

    TEST_CASE.assertEqual(1, error.exception.code)


@pytest.mark.django_db
@pytest.mark.usefixtures(("mock_import_path"))
def test_update_command_with_valid_study_name_and_valid_entity_and_filename(study):
    file_path = Study().import_path().joinpath("instruments/some-instrument.json")

    with TEST_CASE.assertRaises(Instrument.DoesNotExist):
        Instrument.objects.get(name="some-instrument")

    options = get_options(study.name)
    options["entity"] = "instruments.json"
    options["filename"] = file_path

    success, error = update(options)
    TEST_CASE.assertIsNone(error)
    TEST_CASE.assertIsNotNone(success)
    Instrument.objects.get(name="some-instrument")


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_import_path", "period", "analysis_unit")
def test_instrument_import(study, period, analysis_unit):
    with TEST_CASE.assertRaises(Instrument.DoesNotExist):
        Instrument.objects.get(name="some-instrument")

    options = get_options(study.name)
    options["entity"] = "instuments.json"

    _, error = update(options)
    TEST_CASE.assertIsNotNone(error)

    options["entity"] = "instruments"
    success, error = update(options)
    TEST_CASE.assertIsNone(error)
    TEST_CASE.assertIsNotNone(success)

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
    mock_import_path_arguments: PatchImportPathArguments

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
        with patch(
            "ddionrails.workspace.models.basket.settings.BACKUP_DIR",
            self.mock_import_path_arguments["return_value"],
        ):
            manager = StudyImportManager(self.study, redis=False)
            update_single_study(
                self.study, True, clean_import=clean_import, manager=manager
            )

        datasets_ids = [dataset.id for dataset in Dataset.objects.all()]
        self.assertNotIn(self.dataset.id, datasets_ids)

    def test_basket_protection(self):  # pylint: disable=too-many-locals
        """A clean update should leaf baskets intact."""
        clean_import = False

        basket = BasketFactory(name="study_basket")

        manager = StudyImportManager(self.study, redis=False)
        with patch(
            "ddionrails.workspace.models.basket.settings.BACKUP_DIR",
            self.mock_import_path_arguments["return_value"],
        ):
            update_single_study(
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

        import_files = Path(self.mock_import_path_arguments["return_value"])
        new_variables = """study_name,dataset_name,name,concept_name,image_url
some-study,some-dataset,some-variable,some-concept,https://variable-image.de
some-study,some-dataset,some-other-variable,some-concept,https://variable-other-image.de
"""
        with open(import_files.joinpath("variables.csv"), "w", encoding="utf8") as file:
            file.write(new_variables)

        clean_import = True
        manager = StudyImportManager(self.study, redis=False)

        def _enqueue(function_object, *args):
            function_object(*args)

        with patch(
            "ddionrails.imports.management.commands.update.enqueue"
        ) as mocked_enqueue:
            mocked_enqueue.side_effect = _enqueue
            with patch(
                "ddionrails.workspace.models.basket.settings.BACKUP_DIR",
                self.mock_import_path_arguments["return_value"],
            ):
                update_single_study(
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

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for "update" management command for ddionrails project"""

import csv
import logging
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

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
from tests.file_factories import (
    destroy_tmp_path,
    import_data_factory,
    tmp_import_path_with_test_data,
)
from tests.model_factories import (
    BasketFactory,
    DatasetFactory,
    StudyFactory,
    VariableFactory,
)

STUDY_NAME = "some-study"


def get_options(study_name):
    options = {}
    options["study_name"] = study_name
    options["entity"] = []
    options["local"] = True
    options["filename"] = None
    options["clean_import"] = False
    options["no_redis"] = True
    return options


class TestUpdateWithCSV(TestCase):

    def setUp(self) -> None:
        self.tmp_path, patch_dict = tmp_import_path_with_test_data()
        self.import_path_patch = patch(**patch_dict)
        self.import_path_patch.start()
        self.study = StudyFactory(name=STUDY_NAME)
        return super().setUp()

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        destroy_tmp_path(self.tmp_path)
        return super().tearDown()

    def test_update_single_study_local(self):
        local = True
        with open(
            self.tmp_path.joinpath("variables.csv"), encoding="utf8"
        ) as variables_file:
            expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
        manager = StudyImportManager(self.study, redis=False)
        update_single_study(self.study, local, (), None, manager=manager)
        result = {variable.name for variable in Variable.objects.all()}
        self.assertNotEqual(0, len(result))
        result_union = expected_variables.intersection(result)
        self.assertEqual(expected_variables, result_union)

    def test_update_single_study_entity(self):
        entities = ("periods",)

        local = True
        with open(self.tmp_path.joinpath("periods.csv"), encoding="utf8") as periods_file:
            expected_periods = {row["name"] for row in csv.DictReader(periods_file)}
        manager = StudyImportManager(self.study, redis=False)
        update_single_study(self.study, local, entities, None, manager=manager)
        result = {period.name for period in Period.objects.all()}
        self.assertNotEqual(0, len(result))
        # Result can contain more but should contain all from expected
        result_union = expected_periods.intersection(result)
        self.assertEqual(expected_periods, result_union)

    def test_update_single_study(self):
        with open(
            self.tmp_path.joinpath("variables.csv"), encoding="utf8"
        ) as variables_file:
            expected_variables = {row["name"] for row in csv.DictReader(variables_file)}
        update_patch = patch("ddionrails.imports.management.commands.update.set_up_repo")
        mocked_update_repo = update_patch.start()
        manager = StudyImportManager(self.study, redis=False)
        update_single_study(self.study, False, (), "", manager=manager)
        mocked_update_repo.assert_called_once()
        result = {variable.name for variable in Variable.objects.all()}
        update_patch.stop()
        self.assertNotEqual(0, len(result))
        result_union = expected_variables.intersection(result)
        self.assertEqual(expected_variables, result_union)

    def test_update_single_study_entity_filename_without_redis(self):
        filename = Study().import_path().joinpath("instruments/some-instrument.json")
        with patch("django_rq.enqueue") as redis_enqueue:
            with self.assertRaises(SystemExit) as error:
                call_command(
                    "update",
                    self.study.name,
                    "instruments.json",
                    "-f",
                    filename,
                    "-l",
                    "-r",
                )
            self.assertEqual(0, error.exception.code)
            self.assertFalse(redis_enqueue.called)

    def test_update_single_study_entity_nonexistent_filename(self):
        filename = Study().import_path().joinpath("nonexistent-file.json")

        logger = logging.getLogger("ddionrails.imports.manager")
        with unittest.mock.patch.object(logger, "error") as log:
            with self.assertRaises(SystemExit) as error:
                call_command(
                    "update", self.study.name, "instruments.json", "-f", filename, "-l"
                )
            logging.getLogger("ddionrails.imports.manager")
            self.assertEqual(1, error.exception.code)
            log.assert_called_once_with(
                'Study "%s" has no file: "%s"',
                STUDY_NAME,
                "nonexistent-file.json",
            )

    def test_update_command_with_valid_study_name_and_valid_entity_and_filename(self):
        file_path = Study().import_path().joinpath("instruments/some-instrument.json")

        with self.assertRaises(Instrument.DoesNotExist):
            Instrument.objects.get(name="some-instrument")

        options = get_options(self.study.name)
        options["entity"] = "instruments.json"
        options["filename"] = file_path

        success, error = update(options)
        self.assertIsNone(error)
        self.assertIsNotNone(success)
        Instrument.objects.get(name="some-instrument")


class TestStdOutAndStdErr(TestCase):

    def setUp(self) -> None:
        self.std_out = StringIO()
        self.std_err = StringIO()
        self.std_stack = ExitStack()
        self.std_stack.enter_context(redirect_stdout(self.std_out))
        self.std_stack.enter_context(redirect_stderr(self.std_err))
        return super().setUp()

    def tearDown(self) -> None:
        self.std_stack.close()
        return super().tearDown()

    def test_update_command_shows_help(self):
        """Test "update" shows help"""

        for option in ("-h", "--help"):
            with self.assertRaises(SystemExit) as error:
                call_command("update", option)

            self.assertEqual(0, error.exception.code)
            output = self.std_out.getvalue()
            self.assertIn(
                "This command is used to update study metadata in ddionrails.", output
            )
            self.assertIn("--local", output)
            self.assertIn("--filename", output)

    def test_update_command_with_invalid_study_name(self):

        with self.assertRaises(SystemExit) as error:
            call_command("update", "study-not-in-db")

        output = self.std_err.getvalue()
        self.assertEqual(1, error.exception.code)
        self.assertIn("does not exist", output)

    def test_update_command_with_valid_study_name_and_invalid_entity_and_filename(self):
        study = StudyFactory(name=STUDY_NAME)
        filename = "tests/imports/test_data/sample.csv"

        for option in ("-f", "--filename"):

            with self.assertRaises(SystemExit) as error:
                call_command("update", study.name, "periods", option, filename)

            output = self.std_err.getvalue()
            self.assertEqual(1, error.exception.code)
            self.assertRegex(
                output,
                ".*Support for single file import not available for entity.*",
            )


class TestUpdateAllStudiesCompletely(TestCase):

    def setUp(self) -> None:
        self.patcher = patch(
            "ddionrails.imports.management.commands.update.update_all_studies_completely"
        )
        self.patched_function = self.patcher.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.patcher.stop()
        return super().tearDown()

    def test_update_command_without_study_name(self):
        """Test "update" runs "update_all_studies_completely" when given no study name"""
        self.patched_function.reset_mock()
        with self.assertRaises(SystemExit) as error:
            call_command("update")

        self.assertEqual(0, error.exception.code)
        self.patched_function.assert_called_once()

    def test_update_command_without_study_name_local(self):
        """Test "update" runs "update_all_studies_completely" correctly with --local"""
        self.patched_function.reset_mock()
        for option in ("-l", "--local"):
            with self.assertRaises(SystemExit) as error:
                call_command("update", option)

            self.assertEqual(0, error.exception.code)
            self.patched_function.assert_called_once_with(True, False, redis=True)
            self.patched_function.reset_mock()


class TestUpdate(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp_path, cls.patch_dict, cls.files, cls.file_content, cls.study_name = (
            import_data_factory()
        )
        return super().setUpClass()

    def setUp(self):
        self.study = StudyFactory(name=self.study_name)
        self.dataset = DatasetFactory(name="test-dataset", study=self.study)

        self.import_path_patch = patch(**self.patch_dict)
        self.import_path_patch.start()
        self.tmp_backup_path = Path(mkdtemp())
        self.tmp_backup_patch = patch(
            "ddionrails.workspace.models.basket.settings.BACKUP_DIR", self.tmp_backup_path
        )
        self.tmp_backup_patch.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        self.tmp_backup_patch.stop()
        destroy_tmp_path(self.tmp_backup_path)
        return super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        destroy_tmp_path(cls.tmp_path)
        return super().tearDownClass()

    def test_instrument_import(self):
        instrument_data = self.file_content["instruments.csv"][0]
        instrument_name = instrument_data["name"]
        with self.assertRaises(Instrument.DoesNotExist):
            Instrument.objects.get(name=instrument_name)

        period_names = [line["name"] for line in self.file_content["periods.csv"]]
        analysis_unit_names = [
            line["name"] for line in self.file_content["analysis_units.csv"]
        ]

        options = get_options(self.study.name)
        options["entity"] = "periods"
        _, error = update(options)

        options["entity"] = "analysis_units"
        _, error = update(options)

        options = get_options(self.study.name)
        options["entity"] = "instuments.json"

        _, error = update(options)
        self.assertIsNotNone(error)

        options["entity"] = "instruments"
        success, error = update(options)
        self.assertIsNone(error)
        self.assertIsNotNone(success)

        instrument = Instrument.objects.get(name=instrument_name)
        self.assertEqual(instrument_data["type"], instrument.type["en"])
        self.assertEqual(instrument_data["type_de"], instrument.type["de"])
        self.assertEqual(
            str(instrument_data["type_position"]), instrument.type["position"]
        )
        self.assertEqual(instrument_data["mode"], instrument.mode)
        self.assertIn(instrument.period.name, period_names)
        self.assertIn(instrument.analysis_unit.name, analysis_unit_names)

    def test_clean_update(self):
        """Does a clean update remove study data before the update?

        The clean import should remove all entities related to a study before
        the import of the study.
        There is no dat. provided to import for this test.
        After the clean import without data only the study object itself should
        remain in the database.
        The test dataset should be gone.
        """
        clean_import = True
        self.assertTrue(list(Dataset.objects.filter(id=self.dataset.id)))
        manager = StudyImportManager(self.study, redis=False)
        update_single_study(self.study, True, clean_import=clean_import, manager=manager)

        datasets_ids = [dataset.id for dataset in Dataset.objects.all()]
        self.assertNotIn(self.dataset.id, datasets_ids)
        for variable in self.file_content["variables.csv"]:
            Variable.objects.get(dataset__name=variable["dataset"], name=variable["name"])

    def test_basket_protection(self):  # pylint: disable=too-many-locals
        """A clean update should leave baskets intact."""
        clean_import = False

        basket = BasketFactory(name="study_basket", study=self.study)

        manager = StudyImportManager(self.study, redis=False)
        update_single_study(self.study, True, clean_import=clean_import, manager=manager)
        variable_name = self.file_content["variables.csv"][0]["name"]
        variable = Variable.objects.get(name=variable_name)
        outdated_variable = VariableFactory(dataset__study=self.study)
        outdated_variable_name = outdated_variable.name

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

        clean_import = True
        manager = StudyImportManager(self.study, redis=False)

        def _enqueue(function_object, *args):
            function_object(*args)

        with patch(
            "ddionrails.imports.management.commands.update.enqueue"
        ) as mocked_enqueue:
            mocked_enqueue.side_effect = _enqueue
            update_single_study(
                self.study, True, clean_import=clean_import, manager=manager
            )

        with self.assertRaises(ObjectDoesNotExist):
            Variable.objects.get(name=outdated_variable_name)

        variable = Variable.objects.get(name=variable_name)

        self.assertEqual(1, BasketVariable.objects.all().count())

        self.assertEqual(
            1, BasketVariable.objects.filter(variable_id=variable_id).count()
        )
        self.assertEqual(
            0, BasketVariable.objects.filter(variable_id=outdated_id).count()
        )
        self.assertEqual(1, Basket.objects.filter(id=basket_id).count())
        for variable in self.file_content["variables.csv"]:
            Variable.objects.get(dataset__name=variable["dataset"], name=variable["name"])


class TestUpdateNoData(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        Study.objects.all().delete()
        return super().setUpClass()

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.mock_update_single = patch.object(StudyImportManager, "import_single_entity")

        self.mock_single_study = patch(
            "ddionrails.imports.management.commands.update.update_single_study"
        )
        self.single_entity_mocker = self.mock_update_single.start()
        self.single_study_mocker = self.mock_single_study.start()

    def test_update_command_with_valid_study_name_and_invalid_entity(self):
        with self.assertRaises(SystemExit) as error:
            call_command("update", self.study.name, "invalid-entity")

        self.assertEqual(1, error.exception.code)

    def test_update_study_partial(self):
        manager = StudyImportManager(self.study)
        entity = ("periods",)
        update_study_partial(manager, entity)
        self.single_entity_mocker.assert_called_once_with(entity[0])

    def test_update_all_studies_completely(self):
        self.single_study_mocker.reset_mock()
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
            self.assertEqual(0, error.exception.code)
        self.assertEqual(
            "instruments.json", mocked_import_single_entity.call_args.args[0]
        )
        self.assertEqual(Path(filename), mocked_import_single_entity.call_args.args[1])

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
            with self.assertRaises(SystemExit) as error:
                call_command("update", self.study.name, option)

            self.assertEqual(0, error.exception.code)

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

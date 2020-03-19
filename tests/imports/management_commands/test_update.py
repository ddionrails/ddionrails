# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import unittest
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from click.testing import CliRunner
from django.core.management import call_command

from ddionrails.imports.management.commands import update
from ddionrails.imports.manager import StudyImportManager

pytestmark = [pytest.mark.django_db]

TEST_CASE = unittest.TestCase()


@pytest.fixture
def mocked_update_single_study(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_single_study"
    )


@pytest.fixture
def mocked_update_study_partial(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_study_partial"
    )


@pytest.fixture
def mocked_update_all_studies_completely(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_all_studies_completely"
    )


@pytest.fixture
def mocked_import_single_entity(mocker):
    return mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.import_single_entity"
    )


@pytest.fixture
def mocked_import_all_entities(mocker):
    return mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.import_all_entities"
    )


def test_update_study_partial(study, mocked_import_single_entity):
    manager = StudyImportManager(study)
    entity = ("periods",)
    update.update_study_partial(manager, entity)
    mocked_import_single_entity.assert_called_once_with(entity[0])


def test_update_single_study(study, mocker, mocked_import_all_entities):
    mocked_update_repo = mocker.patch(
        "ddionrails.imports.manager.StudyImportManager.update_repo"
    )

    update.update_single_study(study, False, (), None)
    mocked_update_repo.assert_called_once()
    mocked_import_all_entities.assert_called_once()


def test_update_single_study_local(study, mocked_import_all_entities):
    update.update_single_study(study, True, (), None)
    mocked_import_all_entities.assert_called_once()


def test_update_single_study_entity(study, mocked_update_study_partial):
    update.update_single_study(study, True, ("periods",), None)
    mocked_update_study_partial.assert_called_once()


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
    with TEST_CASE.assertRaises(SystemExit):
        call_command("update", "-h")
    output = capsys.readouterr().out
    assert "This command is used to update study metadata in ddionrails." in output
    assert "--local" in output
    assert "--filename" in output


def test_update_command_without_study_name(mocked_update_all_studies_completely):
    """ Test "update" runs "update_all_studies_completely" when given no study name """
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update")
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_all_studies_completely.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_without_study_name_local(
    option, mocked_update_all_studies_completely
):
    """Test "update" runs "update_all_studies_completely" correctly with --local """
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", option)
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_all_studies_completely.assert_called_once_with(True)


def test_update_command_with_invalid_study_name(capsys: CaptureFixture):
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", "study-not-in-db")
        except SystemExit as error:
            TEST_CASE.assertEqual(1, error.code)
            raise error
    TEST_CASE.assertIn("does not exist", capsys.readouterr().err)


def test_update_command_with_valid_study_name(study, mocked_update_single_study):
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", study.name)
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_single_study.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_with_valid_study_name_local(
    study, option, mocked_update_single_study
):
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", study.name, option)
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_single_study.assert_called_once_with(study, True, set(), None)


def test_update_command_with_valid_study_name_and_entity(
    study, mocked_update_single_study
):
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", study.name, "periods")
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_single_study.assert_called_once_with(study, False, {"periods"}, None)


def test_update_command_with_valid_study_name_and_invalid_entity(study):
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", study.name, "invalid-entity")
        except SystemExit as error:
            TEST_CASE.assertEqual(1, error.code)
            raise error


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_valid_entity_and_filename(
    study, option, mocked_update_single_study
):
    filename = "tests/imports/test_data/sample.csv"
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("update", study.name, "instruments", option, filename)
        except SystemExit as error:
            TEST_CASE.assertEqual(0, error.code)
            raise error
    mocked_update_single_study.assert_called_once_with(
        study, False, {"instruments"}, Path(filename)
    )


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_invalid_entity_and_filename(
    study, option, capsys: CaptureFixture
):
    filename = "tests/imports/test_data/sample.csv"
    from io import StringIO

    out = StringIO()
    with TEST_CASE.assertRaises(SystemExit) as error:
        call_command("update", study.name, "periods", option, filename, stdout=out)

    TEST_CASE.assertEqual(error.exception.code, 1)
    TEST_CASE.assertRegex(
        capsys.readouterr().err,
        ".*Support for single file import not available for entity.*",
    )

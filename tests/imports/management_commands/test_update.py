# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import update
from ddionrails.imports.manager import StudyImportManager

pytestmark = [pytest.mark.django_db]


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
def test_update_command_shows_help(option):
    """ Test "update" shows help """
    result = CliRunner().invoke(update.command, option)
    assert 0 == result.exit_code
    assert "This command is used to update study metadata in ddionrails." in result.output
    assert "--local" in result.output
    assert "--filename" in result.output


def test_update_command_without_study_name(mocked_update_all_studies_completely):
    """ Test "update" runs "update_all_studies_completely" when given no study name """
    result = CliRunner().invoke(update.command)
    assert 0 == result.exit_code
    mocked_update_all_studies_completely.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_without_study_name_local(
    option, mocked_update_all_studies_completely
):
    """ Test "update" runs "update_all_studies_completely" when given no study name and --local """
    result = CliRunner().invoke(update.command, option)
    assert 0 == result.exit_code
    mocked_update_all_studies_completely.assert_called_once_with(True)


def test_update_command_with_invalid_study_name():
    result = CliRunner().invoke(update.command, "study-not-in-db")
    assert 1 == result.exit_code
    assert "does not exist" in result.output


def test_update_command_with_valid_study_name(study, mocked_update_single_study):
    result = CliRunner().invoke(update.command, study.name)
    assert 0 == result.exit_code
    mocked_update_single_study.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_with_valid_study_name_local(
    study, option, mocked_update_single_study
):
    result = CliRunner().invoke(update.command, [study.name, option])
    assert 0 == result.exit_code
    mocked_update_single_study.assert_called_once_with(study, True, (), None)


def test_update_command_with_valid_study_name_and_entity(
    study, mocked_update_single_study
):
    result = CliRunner().invoke(update.command, [study.name, "periods"])
    assert 0 == result.exit_code
    mocked_update_single_study.assert_called_once_with(study, False, ("periods",), None)


def test_update_command_with_valid_study_name_and_invalid_entity(study):
    result = CliRunner().invoke(update.command, [study.name, "invalid-entity"])
    assert 1 == result.exit_code


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_valid_entity_and_filename(
    study, option, mocked_update_single_study
):
    filename = "tests/imports/test_data/sample.csv"
    result = CliRunner().invoke(
        update.command, [study.name, "instruments", option, filename]
    )
    assert 0 == result.exit_code
    mocked_update_single_study.assert_called_once_with(
        study, False, ("instruments",), filename
    )


@pytest.mark.parametrize("option", ("-f", "--filename"))
def test_update_command_with_valid_study_name_and_invalid_entity_and_filename(
    study, option
):
    filename = "tests/imports/test_data/sample.csv"
    result = CliRunner().invoke(update.command, [study.name, "periods", option, filename])
    assert 1 == result.exit_code
    assert "Support for single file import not available for entity" in result.output

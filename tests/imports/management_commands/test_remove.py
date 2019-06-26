# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "remove" management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import remove
from ddionrails.studies.models import Study


@pytest.fixture
def mocked_delete_method(mocker):
    """ Mocked Study.delete method for test cases """
    return mocker.patch.object(Study, "delete")


def test_remove_command_without_study_name():
    """ Test remove management command displays "missing argument" message """
    result = CliRunner().invoke(remove.command)
    assert 'Missing argument "STUDY_NAME"' in result.output
    expected = 2
    assert expected == result.exit_code


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_remove_command_displays_help(option):
    """ Test remove management command displays help with "-h" and "--help" """
    result = CliRunner().invoke(remove.command, option)
    assert "STUDY_NAME" in result.output
    expected = 0
    assert expected == result.exit_code


@pytest.mark.django_db
def test_remove_command_with_non_existing_study():
    """ Test remove management command displays "does not exist" message """
    study_name = "some-study"
    result = CliRunner().invoke(remove.command, study_name)
    assert 'Study "some-study" does not exist.' in result.output
    expected = 1
    assert expected == result.exit_code


def test_remove_command_aborts(
    study, mocked_delete_method
):  # pylint: disable=unused-argument
    """ Test remove management command aborts when given "N" as input """
    study_name = "some-study"
    result = CliRunner().invoke(remove.command, study_name, input="N")
    assert 'Study "some-study" was not removed.'
    expected = 0
    assert expected == result.exit_code
    mocked_delete_method.assert_not_called()


def test_remove_command_removes_study(
    study, mocked_delete_method
):  # pylint: disable=unused-argument
    """ Test remove management command removes study when given "y" as input """
    study_name = "some-study"
    result = CliRunner().invoke(remove.command, study_name, input="y")
    assert 'Study "some-study" succesfully removed from database.' in result.output
    expected = 0
    assert expected == result.exit_code
    mocked_delete_method.assert_called_once()


@pytest.mark.parametrize("option", ("-f", "--force"))
def test_remove_command_force_removes_study(
    option, study, mocked_delete_method
):  # pylint: disable=unused-argument
    """ Test remove management command with "-f" and "--force" does not ask for continue """
    study_name = "some-study"
    result = CliRunner().invoke(remove.command, [study_name, option])
    assert 'Study "some-study" succesfully removed from database.' in result.output
    expected = 0
    assert expected == result.exit_code
    mocked_delete_method.assert_called_once()

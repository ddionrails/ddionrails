# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "remove" management command for ddionrails project """

import unittest
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from ddionrails.studies.models import Study

TEST_CASE = unittest.TestCase()


@pytest.fixture(name="mocked_delete_method")
def _mocked_delete_method(mocker):
    """ Mocked Study.delete method for test cases """
    return mocker.patch.object(Study, "delete")


def test_remove_command_without_study_name():
    """ Test remove management command displays "missing argument" message """
    with TEST_CASE.assertRaisesRegex(
        CommandError, "Error: the following arguments are required: study_name"
    ):
        call_command("remove")


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_remove_command_displays_help(option, capsys):
    """ Test remove management command displays help with "-h" and "--help" """
    with TEST_CASE.assertRaises(SystemExit):
        call_command("remove", option)
    TEST_CASE.assertRegex(capsys.readouterr().out, ".*usage:.*-h.*")


@pytest.mark.django_db
def test_remove_command_with_non_existing_study(capsys):
    """ Test remove management command displays "does not exist" message """
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("remove", "some-study")
        except SystemExit as exit_error:
            TEST_CASE.assertEqual(1, exit_error.code)
            TEST_CASE.assertIn(
                'Study "some-study" does not exist.', capsys.readouterr().err
            )
            raise exit_error


def test_remove_command_aborts(
    study, mocked_delete_method, capsys
):  # pylint: disable=unused-argument
    """ Test remove management command aborts when given "N" as input """
    study_name = "some-study"
    with patch("builtins.input", side_effect="N"):
        # command should sys.exit with exit code 0
        with TEST_CASE.assertRaisesRegex(SystemExit, "0"):
            try:
                call_command("remove", study_name)
            except SystemExit as exit_error:
                # command should log before exit
                TEST_CASE.assertIn(
                    'Study "some-study" was not removed.', capsys.readouterr().out
                )
                raise exit_error
    # command should exit without removing study
    mocked_delete_method.assert_not_called()


def test_remove_command_removes_study(
    study, mocked_delete_method, capsys
):  # pylint: disable=unused-argument
    """ Test remove management command removes study when given "y" as input """
    study_name = "some-study"
    with patch("builtins.input", side_effect="Y"):
        call_command("remove", study_name)
        TEST_CASE.assertEqual(
            f'Study "{study.name}" succesfully removed from database.\n',
            capsys.readouterr().out,
        )
    mocked_delete_method.assert_called_once()


@pytest.mark.parametrize("option", ("-y", "--yes"))
def test_remove_command_force_removes_study(
    option, study, mocked_delete_method, capsys
):  # pylint: disable=unused-argument
    """ Test remove management command with "-y" and "--yes" does not ask for continue """
    study_name = "some-study"
    call_command("remove", option, study_name)
    TEST_CASE.assertEqual(
        f'Study "{study.name}" succesfully removed from database.\n',
        capsys.readouterr().out,
    )
    mocked_delete_method.assert_called_once()

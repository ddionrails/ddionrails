# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "add" management command for ddionrails project """

from unittest import TestCase

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from ddionrails.studies.models import Study

TEST_CASE = TestCase()


@pytest.fixture
def mocked_delete_method(mocker):
    """ Mocked Study.delete method for test cases """
    return mocker.patch.object(Study, "delete")


def test_add_command_without_study_name():
    """ Test add management command displays "missing argument" message """
    with TEST_CASE.assertRaisesRegex(
        CommandError, ".*arguments are required: study_name.*"
    ):
        call_command("add")


def test_add_command_without_repo_url():
    """ Test add management command displays "missing argument" message """
    with TEST_CASE.assertRaisesRegex(
        CommandError, ".*arguments are required: repo_url.*"
    ):
        call_command("add", "some-study")


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_add_command_displays_help(option, capsys):
    """ Test add management command displays help with "-h" and "--help" """
    with TEST_CASE.assertRaises(SystemExit):
        call_command("add", option)
    TEST_CASE.assertRegex(capsys.readouterr().out, ".*usage:.*-h.*")


@pytest.mark.django_db
def test_add_command_creates_study_object():
    """ Test add management command creates a study """
    TEST_CASE.assertEqual(0, Study.objects.count())
    study_name = "some-study"
    repo_url = "some-repo-url"
    call_command("add", study_name, repo_url)
    TEST_CASE.assertEqual(1, Study.objects.count())
    study = Study.objects.first()
    TEST_CASE.assertEqual(study_name, study.name)
    TEST_CASE.assertEqual(repo_url, study.repo)


def test_add_command_with_existing_study_name(study):
    """ Test add management command with existing study name """
    TEST_CASE.assertEqual(1, Study.objects.count())
    study_name = study.name
    repo_url = study.repo
    with TEST_CASE.assertRaises(SystemExit):
        try:
            call_command("add", study_name, repo_url)
        except SystemExit as exit_error:
            TEST_CASE.assertEqual(1, exit_error.code)
            raise SystemExit()
    TEST_CASE.assertEqual(1, Study.objects.count())

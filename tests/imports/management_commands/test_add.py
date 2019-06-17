# -*- coding: utf-8 -*-

""" Test cases for "add" management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import add
from ddionrails.studies.models import Study


@pytest.fixture
def mocked_delete_method(mocker):
    """ Mocked Study.delete method for test cases """
    return mocker.patch.object(Study, "delete")


def test_add_command_without_study_name():
    """ Test add management command displays "missing argument" message """
    result = CliRunner().invoke(add.command)
    assert 'Missing argument "STUDY_NAME"' in result.output
    assert 2 == result.exit_code


def test_add_command_without_repo_url():
    """ Test add management command displays "missing argument" message """
    study_name = "some-study"
    result = CliRunner().invoke(add.command, study_name)
    assert 'Missing argument "REPO_URL"' in result.output
    assert 2 == result.exit_code


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_add_command_displays_help(option):
    """ Test add management command displays help with "-h" and "--help" """
    result = CliRunner().invoke(add.command, option)
    assert "STUDY_NAME REPO_URL" in result.output
    assert 0 == result.exit_code


@pytest.mark.django_db
def test_add_command_creates_study_object():
    """ Test add management command creates a study """
    assert 0 == Study.objects.count()
    study_name = "some-study"
    repo_url = "some-repo-url"
    result = CliRunner().invoke(add.command, [study_name, repo_url])
    assert 0 == result.exit_code
    assert 1 == Study.objects.count()
    study = Study.objects.first()
    assert study_name == study.name
    assert repo_url == study.repo


def test_add_command_with_existing_study_name(study):
    """ Test add management command with existing study name """
    assert 1 == Study.objects.count()
    study_name = "some-study"
    repo_url = "some-repo-url"
    result = CliRunner().invoke(add.command, [study_name, repo_url])
    assert 1 == result.exit_code
    assert 1 == Study.objects.count()

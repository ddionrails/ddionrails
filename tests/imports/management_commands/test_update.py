# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import pytest
from click.testing import CliRunner
from git import Repo

from ddionrails.imports.management.commands import update

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


def test_update_command_without_study_name():
    result = CliRunner().invoke(update.command)
    assert "Please enter a study name" in result.output
    assert 1 == result.exit_code


@pytest.mark.parametrize("option", ("-a", "--all"))
def test_update_command_with_all_option(
    option, study, mocker
):  # pylint: disable=unused-argument
    """ Test "update" can update all studies """
    mocked_clone_from = mocker.patch.object(Repo, "clone_from")
    result = CliRunner().invoke(update.command, option)
    assert 0 == result.exit_code
    mocked_clone_from.assert_called_once()


@pytest.mark.parametrize("option", ("-s", "--study"))
def test_update_command_with_study_option(
    option, study, mocker
):  # pylint: disable=unused-argument
    """ Test "update" can update single study """
    mocked_clone_from = mocker.patch.object(Repo, "clone_from")
    result = CliRunner().invoke(update.command, [option, study.name])
    assert 0 == result.exit_code
    mocked_clone_from.assert_called_once()

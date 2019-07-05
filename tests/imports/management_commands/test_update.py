# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for "update" management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import update

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


@pytest.fixture
def mocked_update_all_studies_completely(mocker):
    return mocker.patch(
        "ddionrails.imports.management.commands.update.update_all_studies_completely"
    )


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_update_command_shows_help(option):
    """ Test "update" shows help """
    result = CliRunner().invoke(update.command, option)
    assert 0 == result.exit_code


def test_update_command_without_study_name(mocked_update_all_studies_completely):
    """ Test "update" runs "update_all_studies_completely" when given no study name """
    result = CliRunner().invoke(update.command)
    assert 0 == result.exit_code
    mocked_update_all_studies_completely.assert_called_once()


@pytest.mark.parametrize("option", ("-l", "--local"))
def test_update_command_without_study_name_local(option, mocked_update_all_studies_completely):
    """ Test "update" runs "update_all_studies_completely" when given no study name and --local """
    result = CliRunner().invoke(update.command, option)
    assert 0 == result.exit_code
    mocked_update_all_studies_completely.assert_called_once_with(True)

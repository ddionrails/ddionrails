# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for "system" management command for ddionrails project """

import pytest
from click.testing import CliRunner

from ddionrails.imports.management.commands import system
from ddionrails.imports.manager import Repository, SystemImportManager

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


def test_system_command(mocker):
    mocked_update_or_clone_repo = mocker.patch.object(Repository, "update_or_clone_repo")
    mocked_run_import = mocker.patch.object(SystemImportManager, "run_import")
    result = CliRunner().invoke(system.command)
    assert "System settings succesfully imported" in result.output
    assert 0 == result.exit_code
    mocked_update_or_clone_repo.assert_called_once()
    mocked_run_import.assert_called_once()

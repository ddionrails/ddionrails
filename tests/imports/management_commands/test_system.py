# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Test cases for "system" management command for ddionrails project """

import unittest

import pytest
from django.core.management import call_command

from ddionrails.imports.manager import Repository

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name

TEST_CASE = unittest.TestCase()


def test_system_command(mocker, capsys):
    mocked_run_import = mocker.patch("ddionrails.imports.manager.system_import")
    call_command("system")

    TEST_CASE.assertIn("System settings successfully imported", capsys.readouterr().out)
    mocked_run_import.assert_called_once()

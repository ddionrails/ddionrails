# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Functional test cases for "python manage.py system" """

import unittest

import pytest
from django.core.management import call_command

from ddionrails.base.models import System
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.imports, pytest.mark.functional]  # pylint: disable=invalid-name

TEST_CASE = unittest.TestCase()


class TestSystemImport:
    @pytest.mark.django_db
    def test_import_system(self, settings):
        """ Tests the functionality of the management command 'system'

            it is run via:
                'python manage.py system'

            This script should:
             - download the system settings from github
             - should import the system settings to the database
             - should import the studies from studies.csv to the database
        """
        TEST_CASE.assertEqual(0, Study.objects.count())
        TEST_CASE.assertEqual(0, System.objects.count())

        call_command("system")

        path = settings.IMPORT_REPO_PATH.joinpath("system")
        TEST_CASE.assertTrue(path.exists())
        TEST_CASE.assertEqual(1, Study.objects.count())
        TEST_CASE.assertEqual(1, System.objects.count())

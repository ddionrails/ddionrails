# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Functional test cases for "python manage.py system" """

import pathlib

import pytest
from click.testing import CliRunner

from ddionrails.base.models import System
from ddionrails.imports.management.commands import system
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.imports, pytest.mark.functional]  # pylint: disable=invalid-name


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
        assert 0 == Study.objects.count()
        assert 0 == System.objects.count()

        clirunner = CliRunner()
        result = clirunner.invoke(system.command)
        assert result.exit_code == 0

        path = pathlib.Path(settings.IMPORT_REPO_PATH).joinpath("system")
        assert path.exists()
        assert 1 == Study.objects.count()
        assert 1 == System.objects.count()

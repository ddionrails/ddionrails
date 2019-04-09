from pathlib import Path

import pytest

from ddionrails.base.models import System
from ddionrails.studies.models import Study
from scripts import system

pytestmark = [pytest.mark.imports, pytest.mark.functional]


class TestSystemImport:
    def test_import_system(self, db):
        """ Tests the functionality of the script
            'scripts.system'

            it is run by:
                'paver import_system'
            or
                'python manage.py runscript scripts.system'

            This script should:
             - download the system settings from github
             - should import the system settings to the database
             - should import the studies from studies.csv to the database
        """
        assert Study.objects.count() == 0
        assert System.objects.count() == 0
        system.run()
        path = Path("static/repositories/system")
        assert path.exists()
        assert System.objects.count() == 1
        assert Study.objects.count() == 1

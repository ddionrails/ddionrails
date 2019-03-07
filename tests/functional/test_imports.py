import pytest

from imports.manager import LocalImport
from publications.models import Publication

pytestmark = [pytest.mark.functional]

class TestPublicationImport:
    """ Import publications from CSV file """
    def test_import(self, settings, study):
        """ Test starts with 1 study and 0 publications in database"""
        assert 0 == Publication.objects.count()

        # redirect study data path to test data directory
        settings.IMPORT_REPO_PATH = "tests/functional/test_data/"
        importer = LocalImport(study.name)
        importer.run_import("publications.csv")

        assert 1 == Publication.objects.count()
        publication = Publication.objects.first()

        # assert that attributes are set correctly
        assert "Some Publication" == publication.title
        assert "some-doi" == publication.doi

        # assert that relation via foreign key is set correctly
        assert study == publication.study

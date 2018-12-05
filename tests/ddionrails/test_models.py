import pytest
from django.conf import settings

from ddionrails.models import System

pytestmark = [pytest.mark.ddionrails, pytest.mark.models]


class TestSystemModel:
    def test_repo_url_method(self, system):
        assert system.repo_url() + settings.SYSTEM_REPO_URL

    def test_import_path_method(self, system):
        assert system.import_path() == "static/repositories/system/ddionrails/"

    def test_get_method(self, system):
        result = System.get()
        assert isinstance(result, System)

    def test_get_method_with_creation(self, db):
        result = System.get()
        assert isinstance(result, System)

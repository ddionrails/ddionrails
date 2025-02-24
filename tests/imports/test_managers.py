# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

""" Test cases for ddionrails.imports.manager """

from json import dump
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest
from django.test import TestCase

from ddionrails.imports.manager import _import_home_background, _initialize_studies
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.imports]


@pytest.fixture
def mocked_pull(mocker):
    return mocker.patch("git.remote.Remote.pull")


@pytest.fixture
def mocked_clone_from(mocker):
    return mocker.patch("git.repo.base.Repo.clone_from")


@pytest.fixture
def mocked_exists(mocker):
    return mocker.patch("pathlib.Path.exists")


class TestSystemImport(TestCase):

    def test__import_home_background(self):
        with patch("ddionrails.imports.manager.urlretrieve") as request_mock:
            with patch("ddionrails.imports.manager.settings") as settings_mock:
                settings_mock.HOME_BACKGROUND_IMAGE = "http://test.com"
                settings_mock.STATIC_ROOT = "/some/path"
                _import_home_background()
            request_mock.assert_called_once_with(
                "http://test.com", Path("/some/path/background.png")
            )

    def test__initialize_studies(self):
        study_init_content = [{"name": "test_study", "repo": "https://test.com"}]
        with NamedTemporaryFile() as tmp_file:
            with patch("ddionrails.imports.manager.settings") as settings_mock:
                with open(tmp_file.name, "w", encoding="utf-8") as file:
                    dump(study_init_content, file)
                settings_mock.STUDY_INIT_FILE = tmp_file.name
                _initialize_studies()
                Study.objects.get(name="test_study")

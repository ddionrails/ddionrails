# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for ddionrails.imports.manager """

from json import dump
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest
from django.test import TestCase

from ddionrails.studies.models import Study
from ddionrails.imports.manager import Repository
from ddionrails.imports.manager import _initialize_studies, _import_home_background

pytestmark = [pytest.mark.imports]


@pytest.fixture
def repository(study):
    """ A fixture for a repository """
    return Repository(study)


@pytest.fixture
def mocked_pull(mocker):
    return mocker.patch("git.remote.Remote.pull")


@pytest.fixture
def mocked_clone_from(mocker):
    return mocker.patch("git.repo.base.Repo.clone_from")


@pytest.fixture
def mocked_exists(mocker):
    return mocker.patch("pathlib.Path.exists")


@pytest.fixture
def mocked_list_all_files(mocker):
    return mocker.patch.object(Repository, "list_all_files")


class TestSystemImport(TestCase):

    def test__import_home_background(self):
        with patch("ddionrails.imports.manager.urlretrieve") as request_mock:
            with patch("ddionrails.imports.manager.settings") as settings_mock:
                settings_mock.HOME_BACKGROUND_IMAGE = "http://test.com"
                settings_mock.STATIC_ROOT = "/some/path"
                _import_home_background()
            request_mock.assert_called_once_with("http://test.com", Path("/some/path/background.png"))

    def test__initialize_studies(self):
        study_init_content = [{"name": "test_study", "repo": "https://test.com"}]
        with NamedTemporaryFile() as tmp_file:
            with patch("ddionrails.imports.manager.settings") as settings_mock:
                with open(tmp_file.name, "w", encoding="utf-8") as file:
                    dump(study_init_content, file)
                settings_mock.STUDY_INIT_FILE = tmp_file.name
                _initialize_studies()
                Study.objects.get(name="test_study")


class TestRepository:
    def test_pull_or_clone_method(self, repository, mocked_clone_from):
        repository.pull_or_clone()
        mocked_clone_from.assert_called_once()

    def test_pull_or_clone_method_pull(self, repository, mocked_exists, mocker):
        mocked_exists.return_value = True
        mocked_repo = mocker.patch.object(repository, "repo")
        repository.pull_or_clone()
        mocked_repo.remotes.origin.pull.assert_called_once()

    def test_set_commit_id_method(self, repository, mocker):
        mocked_repo = mocker.patch.object(repository, "repo")
        mocked_repo.head.commit = "12345"
        repository.set_commit_id()
        assert "12345" == repository.study_or_system.current_commit

    def test_set_branch_method(self, repository, mocker, settings):
        mocked_repo = mocker.patch.object(repository, "repo")
        repository.set_branch()
        mocked_repo.git.checkout.assert_called_once_with(settings.IMPORT_BRANCH)

    def test_is_import_required_method(self, repository, mocker):
        mocked_repo = mocker.patch.object(repository, "repo")
        mocked_repo.head.commit = "2"
        repository.study_or_system.current_commit = "1"
        repository.study_or_system.save()
        result = repository.is_import_required()
        expected = True
        assert expected is result

    def test_is_import_required_method_false(self, repository, mocker):
        mocked_repo = mocker.patch.object(repository, "repo")
        mocked_repo.head.commit = "1"
        repository.study_or_system.current_commit = "1"
        repository.study_or_system.save()
        result = repository.is_import_required()
        expected = False
        assert expected is result

    def test_list_changed_files_method(self, repository, mocker):
        mocked_repo = mocker.patch.object(repository, "repo")
        mocked_repo.git.diff.return_value = "1.txt\n2.txt\n"
        result = repository.list_changed_files()
        expected = ["1.txt", "2.txt"]
        assert expected == result

    def test_list_all_files_method(self, repository):
        result = repository.list_all_files()
        assert [] == result

    def test_import_list_method(self, repository, mocker):
        mocked_list_changed_files = mocker.patch.object(Repository, "list_changed_files")
        repository.import_list()
        mocked_list_changed_files.assert_called_once()

    def test_import_list_method_import_all(self, repository, mocker):
        mocked_list_all_files = mocker.patch.object(Repository, "list_all_files")
        repository.import_list(import_all=True)
        mocked_list_all_files.assert_called_once()

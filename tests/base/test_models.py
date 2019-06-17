# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for models in ddionrails.base app """

import pathlib

import pytest

from ddionrails.base.models import System

pytestmark = [pytest.mark.ddionrails, pytest.mark.models]  # pylint: disable=invalid-name


class TestSystemModel:
    def test_repo_url_method(self, system, settings):
        assert system.repo_url() + settings.SYSTEM_REPO_URL

    def test_import_path_method(self, system, settings):
        result = system.import_path()
        path = pathlib.Path(settings.IMPORT_REPO_PATH).joinpath(
            system.name, settings.IMPORT_SUB_DIRECTORY
        )
        expected = str(path) + "/"
        assert expected == result

    def test_get_method(self, system):  # pylint: disable=unused-argument
        result = System.get()
        assert isinstance(result, System)

    def test_get_method_with_creation(
        self, db
    ):  # pylint: disable=unused-argument,invalid-name
        result = System.get()
        assert isinstance(result, System)

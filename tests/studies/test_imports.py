# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

"""Test cases for importer classes in ddionrails.studies app"""

import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from ddionrails.studies.imports import StudyDescriptionImport, StudyImport
from ddionrails.studies.models import Study
from tests.model_factories import StudyFactory


class TestStudyImport(TestCase):
    def test_import_with_valid_data(self):
        study_importer = StudyImport("")
        valid_study_data = {
            "name": "some-study",
            "label": "Some Study",
            "description": "This is some study",
        }
        response = study_importer.import_element(valid_study_data)
        assert isinstance(response, Study)
        assert response.name == valid_study_data["name"]

    def test_import_with_invalid_data(self):
        study_importer = StudyImport("")
        invalid_study_data = {"name": ""}
        response = study_importer.import_element(invalid_study_data)
        assert response is None


class TestStudyDescriptionImport(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.study_description_importer = StudyDescriptionImport("", self.study)
        return super().setUp()

    def test_import_with_valid_data(self):
        self.study_description_importer.content = "some-study-description"
        self.study_description_importer.data = {
            "name": "some-study",
            "label": "Some Study",
            "config": "some-config",
        }
        self.study_description_importer.execute_import()

    def test_import_with_invalid_data(self):
        self.study_description_importer.content = ""
        self.study_description_importer.data = {}
        with pytest.raises((KeyError, ValidationError)):
            self.study_description_importer.execute_import()

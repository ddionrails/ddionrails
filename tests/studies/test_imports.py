# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,no-self-use

""" Test cases for importer classes in ddionrails.studies app """

import pytest
from django.core.exceptions import ValidationError

from ddionrails.studies.imports import StudyDescriptionImport, StudyImport
from ddionrails.studies.models import Study


@pytest.fixture
def filename():
    return "DUMMY.csv"


@pytest.fixture
def study_importer(db, filename):
    """ A study importer """
    return StudyImport(filename)


@pytest.fixture
def study_description_importer(study, filename):
    """ A study description importer """
    return StudyDescriptionImport(filename, study)


class TestStudyImport:
    def test_import_with_valid_data(self, study_importer):
        valid_study_data = dict(
            name="some-study", label="Some Study", description="This is some study"
        )
        response = study_importer.import_element(valid_study_data)
        assert isinstance(response, Study)
        assert response.name == valid_study_data["name"]

    def test_import_with_invalid_data(self, study_importer):
        invalid_study_data = dict(name="")
        response = study_importer.import_element(invalid_study_data)
        assert response is None


class TestStudyDescriptionImport:
    def test_import_with_valid_data(self, mocker, study_description_importer):
        study_description_importer.content = "some-study-description"
        study_description_importer.data = dict(
            name="some-study", label="Some Study", config="some-config"
        )
        study_description_importer.execute_import()

    def test_import_with_invalid_data(self, study_description_importer):
        study_description_importer.content = ""
        study_description_importer.data = dict()
        with pytest.raises((KeyError, ValidationError)):
            study_description_importer.execute_import()

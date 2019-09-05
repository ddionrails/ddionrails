# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for ddionrails.studies.resources """

import pytest
import tablib

from ddionrails.studies.models import Study
from ddionrails.studies.resources import StudyResource

pytestmark = [pytest.mark.django_db, pytest.mark.resources]


@pytest.fixture
def initial_study_tablib_dataset():
    """ A tablib.Dataset containing an initial study """
    headers = ("name", "repo")
    name = "some-study"
    repo = "some-repo-url"
    values = (name, repo)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def study_tablib_dataset():
    """ A tablib.Dataset containing a study """
    headers = ("name", "label", "config", "description")
    name = "some-study"
    label = "Some Study"
    config = {"variables": {"label_table": True, "script_generators": ["soep-stata"]}}
    description = """
        # Some Study
        
        ## Citation
        * **Title:** Some Study
    """
    values = (name, label, config, description)
    return tablib.Dataset(values, headers=headers)


class TestStudyResource:
    def test_resource_import_succeeds(self, initial_study_tablib_dataset):
        assert 0 == Study.objects.count()
        result = StudyResource().import_data(initial_study_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Study.objects.count()

        study = Study.objects.first()

        # test attributes
        name = initial_study_tablib_dataset["name"][0]
        repo = initial_study_tablib_dataset["repo"][0]

        assert name == study.name
        assert repo == study.repo

    def test_resource_import_fails_no_name(self, initial_study_tablib_dataset):
        assert 0 == Study.objects.count()
        row = initial_study_tablib_dataset.lpop()
        row = list(row)
        # remove name from row
        row[0] = ""
        initial_study_tablib_dataset.lpush(row)
        result = StudyResource().import_data(initial_study_tablib_dataset)
        expected = 1
        assert expected == len(result.invalid_rows)
        expected = True
        assert expected is result.has_validation_errors()
        invalid_row = result.invalid_rows[0]
        expected_error = {
            "id": ["This field cannot be null."],
            "name": ["This field cannot be blank."],
        }
        assert expected_error == invalid_row.error_dict
        assert 0 == Study.objects.count()

    def test_resource_update_succeeds(self, study, study_tablib_dataset):

        assert 1 == Study.objects.count()
        result = StudyResource().import_data(study_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Study.objects.count()
        study = Study.objects.first()

        # test attributes
        label = study_tablib_dataset["label"][0]
        config = study_tablib_dataset["config"][0]
        description = study_tablib_dataset["description"][0]

        assert label == study.label
        assert config == study.config
        assert description == study.description

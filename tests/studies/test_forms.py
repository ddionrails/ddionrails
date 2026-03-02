# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for forms in ddionrails.studies app"""

from django.test import TestCase

from ddionrails.studies.forms import StudyForm, StudyInitialForm


class TestStudyForm(TestCase):
    def test_form_without_data(self):
        form = StudyForm(data={})
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self):
        valid_study_data = {
            "name": "some-study",
            "label": "Some Study",
            "description": "This is some study",
        }
        form = StudyForm(data=valid_study_data)
        assert form.is_valid() is True
        study = form.save()
        assert study.name == valid_study_data["name"]


class TestStudyInitialForm(TestCase):
    def test_form_without_data(self):
        invalid_data = {"name": ""}
        form = StudyInitialForm(data=invalid_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self):
        valid_study_data = {"name": "some-study"}
        form = StudyInitialForm(data=valid_study_data)
        assert form.is_valid() is True
        study = form.save()
        assert study.name == valid_study_data["name"]

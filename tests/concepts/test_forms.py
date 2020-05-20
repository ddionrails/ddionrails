# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for forms in ddionrails.concepts app """

import pytest

from ddionrails.concepts.forms import (
    AnalysisUnitForm,
    ConceptForm,
    ConceptualDatasetForm,
    PeriodForm,
    TopicForm,
)

pytestmark = [pytest.mark.concepts, pytest.mark.forms]  # pylint: disable=invalid-name


class TestConceptForm:
    def test_form_with_invalid_data(self, empty_data):
        form = ConceptForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert dict(form.errors) == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_concept_data):
        form = ConceptForm(data=valid_concept_data)
        assert form.is_valid() is True
        concept = form.save()
        assert concept.name == valid_concept_data["name"]

    @pytest.mark.django_db
    def test_form_with_minimal_valid_data(self, minimal_valid_concept_data):
        form = ConceptForm(data=minimal_valid_concept_data)
        assert form.is_valid() is True
        concept = form.save()
        assert concept.name == minimal_valid_concept_data["name"]


class TestPeriodForm:
    def test_form_with_invalid_data(self, empty_data):
        form = PeriodForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_period_data):
        form = PeriodForm(data=valid_period_data)
        assert form.is_valid() is True


class TestAnalysisUnitForm:
    def test_form_with_invalid_data(self, empty_data):
        form = AnalysisUnitForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_analysis_unit_data):
        form = AnalysisUnitForm(data=valid_analysis_unit_data)
        assert form.is_valid() is True
        analysis_unit = form.save()
        assert analysis_unit.name == valid_analysis_unit_data["analysis_unit_name"]


class TestConceptualDatasetForm:
    def test_form_with_invalid_data(self, empty_data):
        form = ConceptualDatasetForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_conceptual_dataset_data):
        form = ConceptualDatasetForm(data=valid_conceptual_dataset_data)
        assert form.is_valid() is True
        conceptual_dataset = form.save()
        assert (
            conceptual_dataset.name
            == valid_conceptual_dataset_data["conceptual_dataset_name"]
        )


class TestTopicForm:
    def test_form_with_invalid_data(self, empty_data):
        form = TopicForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_topic_data):
        form = TopicForm(data=valid_topic_data)
        assert form.is_valid() is True
        topic = form.save()
        assert topic.name == valid_topic_data["name"]

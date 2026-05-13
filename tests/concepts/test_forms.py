# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for forms in ddionrails.concepts app"""

from django.test import TestCase

from ddionrails.concepts.forms import (
    AnalysisUnitForm,
    ConceptForm,
    ConceptualDatasetForm,
    PeriodForm,
    TopicForm,
)
from tests.file_factories import FAKE
from tests.model_factories import StudyFactory


class TestConceptForm(TestCase):

    def test_form_with_invalid_data(self):
        form = ConceptForm(data={})
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert dict(form.errors) == expected_errors

    def test_form_with_valid_data(self):
        valid_concept_data = {
            "name": FAKE.unique.word(),
            "label": FAKE.sentence(),
            "description": FAKE.paragraph(),
        }
        form = ConceptForm(data=valid_concept_data)
        assert form.is_valid() is True
        concept = form.save()
        assert concept.name == valid_concept_data["name"]

    def test_form_with_minimal_valid_data(self):
        minimal_valid_concept_data = {"name": FAKE.unique.word()}
        form = ConceptForm(data=minimal_valid_concept_data)
        self.assertTrue(form.is_valid(), f"{minimal_valid_concept_data} did not validate")
        concept = form.save()
        self.assertEqual(concept.name, minimal_valid_concept_data["name"])

    @classmethod
    def tearDownClass(cls) -> None:
        FAKE.unique.clear()
        return super().tearDownClass()


class TestPeriodForm(TestCase):
    def test_form_with_invalid_data(self):
        form = PeriodForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    def test_form_with_valid_data(self):
        study = StudyFactory()

        valid_period_data = {
            "study": study.id,
            "period_name": FAKE.unique.word(),
            "label": FAKE.sentence(),
            "description": FAKE.paragraph(),
        }
        form = PeriodForm(data=valid_period_data)
        assert form.is_valid() is True

    @classmethod
    def tearDownClass(cls) -> None:
        FAKE.unique.clear()
        return super().tearDownClass()


class TestAnalysisUnitForm(TestCase):

    def test_form_with_invalid_data(self):
        form = AnalysisUnitForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    def test_form_with_valid_data(self):
        study = StudyFactory()

        valid_analysis_unit_data = {
            "study": study.id,
            "analysis_unit_name": FAKE.unique.word(),
            "label": FAKE.sentence(),
            "description": FAKE.paragraph(),
        }

        form = AnalysisUnitForm(data=valid_analysis_unit_data)
        assert form.is_valid() is True
        analysis_unit = form.save()
        assert analysis_unit.name == valid_analysis_unit_data["analysis_unit_name"]

    @classmethod
    def tearDownClass(cls) -> None:
        FAKE.unique.clear()
        return super().tearDownClass()


class TestConceptualDatasetForm(TestCase):

    def test_form_with_invalid_data(self):
        form = ConceptualDatasetForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    def test_form_with_valid_data(self):
        study = StudyFactory()

        valid_conceptual_dataset_data = {
            "study": study.id,
            "conceptual_dataset_name": FAKE.unique.word(),
            "label": FAKE.sentence(),
            "description": FAKE.paragraph(),
        }
        form = ConceptualDatasetForm(data=valid_conceptual_dataset_data)
        assert form.is_valid() is True
        conceptual_dataset = form.save()
        assert (
            conceptual_dataset.name
            == valid_conceptual_dataset_data["conceptual_dataset_name"]
        )

    @classmethod
    def tearDownClass(cls) -> None:
        FAKE.unique.clear()
        return super().tearDownClass()


class TestTopicForm(TestCase):
    def test_form_with_invalid_data(self):
        form = TopicForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
        }
        assert dict(form.errors) == expected_errors

    def test_form_with_valid_data(self):
        study = StudyFactory()
        valid_topic_data = {"name": FAKE.unique.word(), "study": study.id}
        form = TopicForm(data=valid_topic_data)
        assert form.is_valid() is True
        topic = form.save()
        assert topic.name == valid_topic_data["name"]

    @classmethod
    def tearDownClass(cls) -> None:
        FAKE.unique.clear()
        return super().tearDownClass()

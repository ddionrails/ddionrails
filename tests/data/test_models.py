# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name,too-many-public-methods

"""Test cases for models in ddionrails.data app"""

from typing import OrderedDict

import pytest
from django.test import TestCase

from ddionrails.data.models import Variable
from tests.model_factories import (
    ConceptFactory,
    DatasetFactory,
    StudyFactory,
    TransformationFactory,
    VariableFactory,
)


@pytest.fixture(name="related_variables_by_concept")
def _related_variables_by_concept(variable, concept):
    """Two variables that are related by concept"""
    variable.concept = concept
    variable.save()
    other_variable = VariableFactory(name="other-variable")
    other_variable.concept = concept
    other_variable.save()
    return variable, other_variable


class TestVariable(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.transformation = TransformationFactory()
        cls.variable = cls.transformation.origin
        cls.target_variable = cls.transformation.target
        return super().setUpClass()

    def test_target_variables_dict(self):
        """Define target_variables_dict property structure."""
        origin_variable = self.variable
        target_variable = self.target_variable
        result = origin_variable.target_variables_dict
        expected = OrderedDict([(target_variable.period.name, [target_variable])])
        self.assertDictEqual(expected, result)

    def test_origin_variables_dict(self):
        """Define origin_variables_dict property structure."""
        origin_variable = self.variable
        target_variable = self.target_variable
        result = target_variable.origin_variables_dict
        expected = {origin_variable.period.name: [origin_variable]}
        self.assertEqual(expected, result)

    def test_sorting(self):
        """Variables should be sortable by their name."""
        first_variable = Variable()
        first_variable.name = "a"
        second_variable = Variable()
        second_variable.name = "z"
        variables = [second_variable, first_variable]
        variables.sort()
        self.assertEqual(first_variable, variables[0])
        self.assertEqual(second_variable, variables[1])

    def test_sorting_error(self):
        first_variable = Variable()
        first_variable.name = "a"
        second_variable = "z"
        variables = [second_variable, first_variable]

        with self.assertRaises(TypeError):
            variables.sort()


class TestVariableModel(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.study = StudyFactory()
        cls.concept = ConceptFactory(topics__study=cls.study)
        cls.variable = VariableFactory(concept=cls.concept, dataset__study=cls.study)
        cls.related_variable = VariableFactory(
            concept=cls.concept, dataset__study=cls.study
        )
        return super().setUpClass()

    def test_absolute_url_method(self):
        expected = (
            f"/{self.variable.dataset.study.name}"
            f"/datasets/"
            f"{self.variable.dataset.name}/{self.variable.name}"
        )
        assert self.variable.get_absolute_url() == expected

    def test_get_method(self):
        select_dictionary = {
            "study_name": self.variable.dataset.study.name,
            "dataset_name": self.variable.dataset.name,
            "name": self.variable.name,
        }
        result = self.variable.get(parameters=select_dictionary)
        assert self.variable == result

    def test_get_study(self):
        result = self.variable.get_study()
        expected = self.variable.dataset.study
        assert expected == result

    def test_get_study_with_id(self):
        result = self.variable.get_study(study_id=True)
        expected = self.variable.dataset.study.id
        assert expected == result

    def test_get_concept(self):
        result = self.variable.get_concept()
        expected = self.variable.concept
        assert expected == result

    def test_get_concept_id(self):
        result = self.variable.get_concept(concept_id=True)
        expected = self.variable.concept.id
        assert expected == result

    def test_get_concept_default(self):
        variable = VariableFactory()
        variable.concept = None

        result = variable.get_concept(default="no-concept", concept_id=True)
        expected = "no-concept"
        assert expected == result

    def test_get_related_variables_without_concept(self):
        variable = VariableFactory()
        variable.concept = None
        result = variable.get_related_variables()
        expected = []
        assert expected == result

    def test_get_related_variables_with_concept(self):
        variable = self.variable
        other_variable = self.related_variable
        result = list(variable.get_related_variables())
        # a variable is related to itself?
        expected = [other_variable, variable]
        assert sorted(expected) == sorted(result)

    def test_category_list_method_without_categories(self):
        variable = VariableFactory()
        variable.categories = {}
        assert [] == variable.category_list

    def test_category_list_method(self):
        result = self.variable.category_list
        categories = self.variable.categories
        expected = [
            {
                "value": "1",
                "label": categories["labels"][1],
                "frequency": categories["frequencies"][1],
                "valid": True,
                "label_de": categories["labels_de"][1],
            },
            {
                "value": "-6",
                "label": categories["labels"][0],
                "frequency": categories["frequencies"][0],
                "valid": False,
                "label_de": categories["labels_de"][0],
            },
        ]

        self.assertEqual(expected, result)

    def test_is_categorical_method(self):
        assert self.variable.is_categorical()

    def test_is_categorical_method_fails(self):
        variable = VariableFactory(categories={})
        assert not variable.is_categorical()

    def test_has_translations(self):
        result = self.variable.has_translations()
        assert True is result

    def test_translation_languages(self):
        result = self.variable.translation_languages()
        assert ["de"] == result

    def test_translation_table(self):
        result = self.variable.translation_table()
        categories = self.variable.categories
        expected = {
            "-6": {
                "en": categories["labels"][0],
                "de": categories["labels_de"][0],
            },
            "1": {"en": categories["labels"][1], "de": categories["labels_de"][1]},
        }
        assert expected == result

    def test_content_dict(self):
        result = self.variable.content_dict
        assert result["name"] == self.variable.name
        assert result["scale"] == self.variable.scale
        assert result["uni"] == self.variable.categories


class TestDatasetModel(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = DatasetFactory()
        return super().setUpClass()

    def test_absolute_url_method(self):
        expected = f"/{self.dataset.study.name}/datasets/{self.dataset.name}/"
        assert self.dataset.get_absolute_url() == expected

    def test_direct_url_method(self):
        expected = f"/dataset/{self.dataset.id}"
        assert self.dataset.get_direct_url() == expected

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name,too-many-public-methods

""" Test cases for models in ddionrails.data app """

import unittest

import pytest

from ddionrails.data.models import Transformation, Variable
from tests.data.factories import VariableFactory

pytestmark = [pytest.mark.data, pytest.mark.models]


@pytest.fixture(name="related_variables_by_concept")
def _related_variables_by_concept(variable, concept):
    """ Two variables that are related by concept """
    variable.concept = concept
    variable.save()
    other_variable = VariableFactory(name="other-variable")
    other_variable.concept = concept
    other_variable.save()
    return variable, other_variable


@pytest.mark.django_db
@pytest.mark.usefixtures("variable")
class TestVariable(unittest.TestCase):

    variable: Variable

    def test_target_variables_dict(self):
        """Define target_variables_dict property structure."""
        origin_variable = self.variable
        target_variable = self._target_variable
        result = origin_variable.target_variables_dict
        expected = {
            target_variable.dataset.study.name: {
                target_variable.period.name: [target_variable]
            }
        }
        self.assertEqual(expected, result)

    def test_origin_variables_dict(self):
        """Define origin_variables_dict property structure."""
        origin_variable = self.variable
        target_variable = self._target_variable
        result = target_variable.origin_variables_dict
        expected = {
            origin_variable.dataset.study.name: {
                origin_variable.period.name: [origin_variable]
            }
        }
        self.assertEqual(expected, result)

    @property
    def _target_variable(self) -> Variable:
        _transformation = Transformation()
        _target = Variable()
        _target.name = "some-other-variable"
        _target.dataset = self.variable.dataset
        _target.save()
        _transformation.target = _target
        _transformation.origin = self.variable
        _transformation.save()
        return _target

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


class TestVariableModel:
    def test_string_method(self, variable):
        expected = (
            f"/{variable.dataset.study.name}/data/{variable.dataset.name}/{variable.name}"
        )
        assert str(variable) == expected

    def test_absolute_url_method(self, variable):
        expected = (
            f"/{variable.dataset.study.name}/data/{variable.dataset.name}/{variable.name}"
        )
        assert variable.get_absolute_url() == expected

    def test_get_method(self, variable):
        select_dictionary = dict(
            study_name=variable.dataset.study.name,
            dataset_name=variable.dataset.name,
            name=variable.name,
        )
        result = Variable.get(parameters=select_dictionary)
        assert variable == result

    def test_get_study(self, variable):
        result = variable.get_study()
        expected = variable.dataset.study
        assert expected == result

    def test_get_study_with_id(self, variable):
        result = variable.get_study(study_id=True)
        expected = variable.dataset.study.id
        assert expected == result

    def test_get_concept(self, variable, concept):
        variable.concept = concept
        variable.save()
        result = variable.get_concept()
        expected = variable.concept
        assert expected == result

    def test_get_concept_id(self, variable, concept):
        variable.concept = concept
        variable.save()
        result = variable.get_concept(concept_id=True)
        expected = variable.concept.id
        assert expected == result

    def test_get_concept_default(self, variable):
        result = variable.get_concept(default="no-concept", concept_id=True)
        expected = "no-concept"
        assert expected == result

    def test_period_fallback(self, variable: Variable):
        result = variable.period_fallback
        expected = variable.period
        assert expected == result
        variable.period = None
        result = variable.period_fallback
        expected = variable.dataset.period
        assert expected == result

    def test_get_related_variables_without_concept(self, variable):
        result = variable.get_related_variables()
        expected = []
        assert expected == result

    def test_get_related_variables_with_concept(self, related_variables_by_concept):
        variable, other_variable = related_variables_by_concept
        variable = update_variable(variable)
        other_variable = update_variable(other_variable)
        result = list(variable.get_related_variables())
        # a variable is related to itself?
        expected = [other_variable, variable]
        assert sorted(expected) == sorted(result)

    def test_get_related_variables_by_period_empty(self, variable: Variable):
        result = variable.get_related_variables_by_period()
        expected = {variable.dataset.period.name: []}
        assert expected == result

    def test_get_related_variables_by_period(self, related_variables_by_concept):
        variable, other_variable = related_variables_by_concept
        result = variable.get_related_variables_by_period()
        assert sorted([other_variable, variable]) == sorted(
            result[other_variable.dataset.period.name]
        )

    def test_get_related_variables_by_period_none_period(
        self, related_variables_by_concept
    ):
        variable, other_variable = related_variables_by_concept
        other_variable.dataset.period = None
        other_variable.dataset.save()
        # Refresh variable to sync dataset across both variables
        variable = Variable.objects.get(id=variable.id)
        # Save method should make variable.period == variable.dataset.period
        variable.save()
        other_variable.save()
        result = variable.get_related_variables_by_period()
        assert sorted([other_variable, variable]) == sorted(result["none"])

    def test_category_list_method_without_categories(self, variable):
        variable.categories = {}
        variable.save()
        assert [] == variable.category_list

    def test_category_list_method(self, variable):
        result = variable.category_list
        expected = {
            "value": "-6",
            "label": "[-6] Version of questionnaire with modified filtering",
            "label_de": "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
            "frequency": 1,
            "valid": False,
        }
        assert expected in result

    def test_category_list_method_without_labels_de(self, variable):
        variable.categories.pop("labels_de")
        variable.save()
        result = variable.category_list
        expected = {
            "value": "-6",
            "label": "[-6] Version of questionnaire with modified filtering",
            "label_de": "[-6] Version of questionnaire with modified filtering",
            "frequency": 1,
            "valid": False,
        }
        assert expected in result

    def test_is_categorical_method(self, variable):
        variable.categories = dict(labels="some-category")
        variable.save()
        assert variable.is_categorical()

    def test_is_categorical_method_fails(self, variable):
        variable.categories = dict()
        variable.save()
        assert not variable.is_categorical()

    def test_has_translations(self, variable):
        result = variable.has_translations()
        assert True is result

    def test_translation_languages(self, variable):
        result = variable.translation_languages()
        assert ["de"] == result

    def test_translation_table(self, variable):
        result = variable.translation_table()
        expected = {
            "-6": {
                "en": "[-6] Version of questionnaire with modified filtering",
                "de": "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
            },
            "1": {"en": "[1] Yes", "de": "[1] Ja"},
        }
        assert expected == result

    def test_content_dict(self, variable):
        result = variable.content_dict
        assert result["name"] == variable.name
        assert result["scale"] == variable.scale
        assert result["uni"] == variable.categories

    def test_to_topic_dict(self, variable):
        result = variable.to_topic_dict()
        expected = dict(
            key=f"variable_{variable.id}",
            name=variable.name,
            title=variable.label,
            concept_key=None,
            type="variable",
        )
        assert expected == result

    def test_to_topic_dict_de(self, variable):
        result = variable.to_topic_dict("de")["title"]
        expected = variable.label_de
        assert expected == result

    def test_to_topic_dict_concept(self, variable, concept):
        variable.concept = concept
        variable.save()
        result = variable.to_topic_dict()["concept_key"]
        expected = f"concept_{concept.name}"
        assert expected == result


class TestDatasetModel:
    def test_string_method(self, dataset):
        expected = f"/{dataset.study.name}/data/{dataset.name}"
        assert str(dataset) == expected

    def test_absolute_url_method(self, dataset):
        expected = f"/{dataset.study.name}/data/{dataset.name}"
        assert dataset.get_absolute_url() == expected


def update_variable(variable: Variable) -> Variable:
    """Sync variable with database content."""
    return Variable.objects.get(id=variable.id)

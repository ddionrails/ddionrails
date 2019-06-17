# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for models in ddionrails.data app """

import pytest

from ddionrails.data.models import Variable


pytestmark = [pytest.mark.data, pytest.mark.models]  # pylint: disable=invalid-name


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
        result = Variable.get(x=select_dictionary)
        assert variable == result

    def test_get_study(self, variable):
        result = variable.get_study()
        expected = variable.dataset.study
        assert expected == result

    def test_get_study_with_id(self, variable):
        result = variable.get_study(id=True)
        expected = variable.dataset.study.id
        assert expected == result

    def test_get_concept(self, variable, concept):
        variable.concept = concept
        variable.save()
        result = variable.get_concept()
        expected = variable.concept
        assert expected == result

    def test_get_concept_with_id(self, variable, concept):
        variable.concept = concept
        variable.save()
        result = variable.get_concept(id=True)
        expected = variable.concept.id
        assert expected == result

    def test_get_period(self, variable):
        result = variable.get_period()
        expected = variable.dataset.period
        assert expected == result

    def test_get_period_without_id(self, variable):
        result = variable.get_period()
        expected = variable.dataset.period
        assert expected == result

    def test_get_categories_method_without_categories(self, variable):
        variable.categories = []
        variable.save()
        assert [] == variable.get_categories()

    def test_get_categories_method(self, variable):
        result = variable.get_categories()
        expected = {
            "value": "-6",
            "label": "[-6] Version of questionnaire with modified filtering",
            "label_de": "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
            "frequency": 1,
            "valid": False,
        }
        assert expected == result[0]

    def test_is_categorical_method(self, variable):
        variable.categories = [dict(label="some-category")]
        variable.save()
        assert True is variable.is_categorical()

    def test_is_categorical_method_fails(self, variable):
        variable.categories = dict()
        variable.save()
        assert False is variable.is_categorical()

    def test_has_translations(self, variable):
        result = variable.has_translations()
        assert True is result

    def test_translation_languages(self, variable):
        result = variable.translation_languages()
        assert ["de"] == result

    def test_translation_table(self, variable):
        result = variable.translation_table()
        expected = {
            "label": {"en": variable.label, "de": variable.label_de},
            "-6": {
                "en": "[-6] Version of questionnaire with modified filtering",
                "de": "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
            },
            "1": {"en": "[1] Yes", "de": "[1] Ja"},
        }
        assert expected == result

    def test_to_dict(self, variable):
        result = variable.to_dict()
        assert result["name"] == variable.name
        assert result["scale"] == variable.scale
        assert result["uni"] == variable.categories


class TestDatasetModel:
    def test_string_method(self, dataset):
        expected = f"/{dataset.study.name}/data/{dataset.name}"
        assert str(dataset) == expected

    def test_absolute_url_method(self, dataset):
        expected = f"/{dataset.study.name}/data/{dataset.name}"
        assert dataset.get_absolute_url() == expected

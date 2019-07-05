# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for models in ddionrails.data app """

import pytest

from ddionrails.data.models import Variable

pytestmark = [pytest.mark.data, pytest.mark.models]


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

    def test_get_period(self, variable):
        result = variable.get_period()
        expected = variable.dataset.period
        assert expected == result

    def test_get_period_id(self, variable):
        result = variable.get_period(period_id=True)
        expected = variable.dataset.period.id
        assert expected == result

    def test_get_period_name(self, variable):
        result = variable.get_period(period_id="name")
        expected = variable.dataset.period.name
        assert expected == result

    def test_get_period_default(self, variable):
        variable.dataset.period = None
        variable.dataset.save()
        result = variable.get_period()
        expected = None
        assert expected is result

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

    def test_get_categories_method_without_labels_de(self, variable):
        variable.categories.pop("labels_de")
        variable.save()
        result = variable.get_categories()
        expected = {
            "value": "-6",
            "label": "[-6] Version of questionnaire with modified filtering",
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

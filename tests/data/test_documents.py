# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.data app """

from unittest import TestCase

import pytest
from django.forms.models import model_to_dict

from ddionrails.data.documents import VariableDocument

pytestmark = [pytest.mark.search]

TEST_CASE = TestCase()


@pytest.mark.usefixtures("variables_index")
def test_variable_search_document_fields(variable):
    search = VariableDocument.search().query("match_all")

    expected = 1
    TEST_CASE.assertEqual(expected, search.count())
    response = search.execute()
    document = response.hits[0]

    # test meta
    TEST_CASE.assertEqual(str(variable.id), document.meta.id)
    TEST_CASE.assertEqual("testing_variables", document.meta.index)

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        variable,
        fields=(
            "name",
            "label",
            "label_de",
            "description",
            "description_de",
        ),
    )
    expected["categories"] = {"labels": ["Yes"], "labels_de": ["Ja"]}
    # add facets to expected dictionary
    expected["analysis_unit"] = {
        "label": "Not Categorized",
        "label_de": "Nicht Kategorisiert",
    }
    expected["conceptual_dataset"] = {
        "label": "Not Categorized",
        "label_de": "Nicht Kategorisiert",
    }
    expected["period"] = {"label": "Not Categorized", "label_de": "Nicht Kategorisiert"}
    expected["id"] = str(variable.id)
    expected["study_name"] = variable.dataset.study.title()
    expected["study"] = {
        "name": variable.dataset.study.name,
        "label": variable.dataset.study.label,
    }
    expected["study_name_de"] = ""

    # add relations to expected dictionary
    expected["dataset"] = {"name": variable.dataset.name, "label": variable.dataset.label}
    # generate result dictionary from search document
    result = document.to_dict()
    for key, value in expected.items():
        TEST_CASE.assertEqual(value, result[key], msg=f"Problem in {key}")
    for key in result.keys():
        TEST_CASE.assertIn(key, expected)


@pytest.mark.usefixtures("variables_index")
def test_variable_search_document_fields_missing_related_objects(variable):
    variable.dataset.analysis_unit = None
    variable.dataset.conceptual_dataset = None
    variable.dataset.period = None
    variable.dataset.save()
    variable.save()

    search = VariableDocument.search().query("match_all")
    response = search.execute()
    document = response.hits[0]

    expected = "Not Categorized"
    TEST_CASE.assertEqual(expected, document.analysis_unit.label)
    TEST_CASE.assertEqual(expected, document.conceptual_dataset.label)
    TEST_CASE.assertEqual(expected, document.period.label)


@pytest.mark.usefixtures("variables_index")
def test_variable_search_document_fields_string_representing_missing(
    variable, conceptual_dataset, analysis_unit, period
):
    analysis_unit.label = "Unspecified"
    analysis_unit.save()
    conceptual_dataset.label = "none"
    conceptual_dataset.save()
    period.label = "unspecified"
    period.save()

    variable.dataset.analysis_unit = analysis_unit
    variable.dataset.conceptual_dataset = conceptual_dataset
    variable.dataset.period = period
    variable.dataset.save()
    variable.save()

    search = VariableDocument.search().query("match_all")
    response = search.execute()
    document = response.hits[0]

    excepted = "Not Categorized"
    TEST_CASE.assertEqual(excepted, document.analysis_unit.label)
    TEST_CASE.assertEqual(excepted, document.conceptual_dataset.label)
    TEST_CASE.assertEqual(excepted, document.period.label)

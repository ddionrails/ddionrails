# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.data app """

from unittest import TestCase

import pytest
from django.forms.models import model_to_dict

from ddionrails.data.documents import VariableDocument

pytestmark = [pytest.mark.search]

TEST_CASE = TestCase()


def test_variable_search_document_fields(
    variables_index, variable  # pylint: disable=unused-argument
):
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
            "description_long",
        ),
    )
    expected["categories"] = {
        key: variable.categories.get(key) for key in ("labels", "labels_de")
    }
    # add facets to expected dictionary
    expected["analysis_unit"] = variable.dataset.analysis_unit.title()
    expected["conceptual_dataset"] = variable.dataset.conceptual_dataset.title()
    expected["period"] = variable.dataset.period.title()
    expected["study"] = variable.dataset.study.title()

    # add relations to expected dictionary
    expected["dataset"] = variable.dataset.name
    expected["type"] = "variable"
    # generate result dictionary from search document
    result = document.to_dict()
    TEST_CASE.assertEqual(expected, result)


@pytest.mark.usefixture("variable_index")
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
    TEST_CASE.assertEqual(expected, document.analysis_unit)
    TEST_CASE.assertEqual(expected, document.conceptual_dataset)
    TEST_CASE.assertEqual(expected, document.period)


@pytest.mark.usefixture("variable_index")
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

    expected = "Not Categorized"
    TEST_CASE.assertEqual(expected, document.analysis_unit)
    TEST_CASE.assertEqual(expected, document.conceptual_dataset)
    TEST_CASE.assertEqual(expected, document.period)

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.data app """

import pytest
from django.forms.models import model_to_dict

from ddionrails.data.documents import VariableDocument

pytestmark = [pytest.mark.search]


def test_variable_search_document_fields(
    variables_index, variable  # pylint: disable=unused-argument
):
    search = VariableDocument.search().query("match", name="some-concept")

    expected = 1
    assert expected == search.count()
    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(variable.id) == document.meta.id
    assert "testing_variables" == document.meta.index

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
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result


def test_variable_search_document_fields_missing_related_objects(
    variables_index, variable  # pylint: disable=unused-argument
):
    variable.dataset.analysis_unit = None
    variable.dataset.conceptual_dataset = None
    variable.dataset.period = None
    variable.dataset.save()
    variable.save()

    search = VariableDocument.search().query("match", name="some-concept")
    response = search.execute()
    document = response.hits[0]

    assert "None" == document.analysis_unit
    assert "None" == document.conceptual_dataset
    assert "None" == document.period

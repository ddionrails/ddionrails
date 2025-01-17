# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.instruments app """

import pytest
from django.forms.models import model_to_dict

from ddionrails.instruments.documents import QuestionDocument

pytestmark = [pytest.mark.search]


@pytest.mark.usefixtures("questions_index")
def test_question_search_document_fields(question):
    search = QuestionDocument.search().query("match_all")

    expected_count = 1
    assert expected_count == search.count()
    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(question.id) == document.meta.id
    assert document.meta.index in (
        "testing_questions",
        "questions" == document.meta.index,
    )

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        question, fields=("name", "label", "label_de", "description", "description_de")
    )
    expected["label"] = question.label
    # add facets to expected dictionary
    expected["analysis_unit"] = {
        "label": "Not Categorized",
        "label_de": "Nicht Kategorisiert",
    }
    expected["period"] = {"label": "Not Categorized", "label_de": "Nicht Kategorisiert"}
    expected["study_name"] = question.instrument.study.title()
    expected["study"] = {
        "name": question.instrument.study.name,
        "label": question.instrument.study.label,
    }
    expected["study_name_de"] = ""
    expected["question_items"] = [{}]

    expected["instrument"] = {
        "name": question.instrument.name,
        "label": question.instrument.label,
        "label_de": question.instrument.label_de,
    }
    expected["id"] = str(question.id)
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result


def test_variable_search_document_fields_missing_related_objects(
    questions_index, question  # pylint: disable=unused-argument
):
    question.instrument.analysis_unit = None
    question.instrument.period = None
    question.instrument.save()
    question.save()

    search = QuestionDocument.search().query("match_all")
    response = search.execute()
    document = response.hits[0]

    expected = {"label": "Not Categorized", "label_de": "Nicht Kategorisiert"}
    assert expected == document.analysis_unit
    assert expected == document.period

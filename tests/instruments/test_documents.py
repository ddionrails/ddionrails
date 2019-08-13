# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.instruments app """

import pytest
from django.forms.models import model_to_dict

from ddionrails.instruments.documents import QuestionDocument

pytestmark = [pytest.mark.search]


def test_question_search_document_fields(
    questions_index, question  # pylint: disable=unused-argument
):
    search = QuestionDocument.search().query("match_all")

    expected = 1
    assert expected == search.count()
    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(question.id) == document.meta.id
    assert "testing_questions" == document.meta.index

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        question, fields=("name", "label", "label_de", "description", "description_de")
    )
    expected["label"] = question.label
    # add facets to expected dictionary
    expected["analysis_unit"] = question.instrument.analysis_unit.title()
    expected["period"] = question.instrument.period.title()
    expected["study"] = question.instrument.study.title()

    expected["instrument"] = question.instrument.title()
    expected["type"] = "question"
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

    expected = None
    assert expected is document.analysis_unit
    assert expected is document.period

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for documents in ddionrails.instruments app"""

from django.forms.models import model_to_dict
from django.test import LiveServerTestCase

from ddionrails.instruments.documents import QuestionDocument
from tests.functional.search_index_fixtures import set_up_index, tear_down_index
from tests.model_factories import QuestionFactory


class TestQuestionDocuments(LiveServerTestCase):

    def setUp(self) -> None:
        tear_down_index(self, "questions")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "questions")
        return super().tearDown()

    def test_question_search_document_fields(self):
        question = QuestionFactory(
            question_items__size=2,
        )
        set_up_index(self, question, "questions")

        search = QuestionDocument.search().query("match_all")

        expected_count = 1
        assert expected_count == search.count()
        response = search.execute()
        document = response.hits[0]

        # test meta
        assert str(question.id) == document.meta.id
        assert document.meta.index in (
            "testing_questions",
            "questions",
        )

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            question,
            fields=("name", "label", "label_de", "description", "description_de"),
        )
        expected["label"] = question.label
        # add facets to expected dictionary
        expected["analysis_unit"] = {
            "label": question.instrument.analysis_unit.label,
            "label_de": question.instrument.analysis_unit.label_de,
        }
        expected["period"] = {
            "label": question.instrument.period.label,
            "label_de": question.instrument.period.label_de,
        }
        expected["study_name"] = question.instrument.study.label
        expected["study"] = {
            "name": question.instrument.study.name,
            "label": question.instrument.study.label,
            "label_de": question.instrument.study.label_de,
        }
        expected["study_name_de"] = question.instrument.study.label_de
        expected["question_items"] = {"en": [], "de": []}
        for item in question.question_items.all():
            expected["question_items"]["en"].append(item.label)
            expected["question_items"]["de"].append(item.label_de)

        expected["instrument"] = {
            "name": question.instrument.name,
            "label": question.instrument.label,
            "label_de": question.instrument.label_de,
        }
        expected["id"] = str(question.id)
        # generate result dictionary from search document
        result = document.to_dict()
        assert expected == result

    def test_variable_search_document_fields_missing_related_objects(self):
        question = QuestionFactory(
            question_items__size=2,
            instrument__analysis_unit=None,
            instrument__period=None,
        )
        set_up_index(self, question, "questions")

        search = QuestionDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        expected = {"label": "Not Categorized", "label_de": "Nicht Kategorisiert"}
        assert expected == document.analysis_unit
        assert expected == document.period

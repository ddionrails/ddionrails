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
        self.question = QuestionFactory(question_items__size=1)
        set_up_index(self, self.question, "questions")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "questions")
        return super().tearDown()

    def test_question_search_document_fields(self):
        search = QuestionDocument.search().query("match_all")

        expected_count = 1
        assert expected_count == search.count()
        response = search.execute()
        document = response.hits[0]

        # test meta
        assert str(self.question.id) == document.meta.id
        assert document.meta.index in (
            "testing_questions",
            "questions",
        )

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            self.question,
            fields=("name", "label", "label_de", "description", "description_de"),
        )
        expected["label"] = self.question.label
        # add facets to expected dictionary
        expected["analysis_unit"] = {
            "label": "Not Categorized",
            "label_de": "Nicht Kategorisiert",
        }
        expected["period"] = {
            "label": "Not Categorized",
            "label_de": "Nicht Kategorisiert",
        }
        expected["study_name"] = self.question.instrument.study.label
        expected["study"] = {
            "name": self.question.instrument.study.name,
            "label": self.question.instrument.study.label,
            "label_de": self.question.instrument.study.label_de,
        }
        expected["study_name_de"] = self.question.instrument.study.label_de
        # TODO: Add question item to test
        # expected["question_items"] = {"en": [], "de": []}

        expected["instrument"] = {
            "name": self.question.instrument.name,
            "label": self.question.instrument.label,
            "label_de": self.question.instrument.label_de,
        }
        expected["id"] = str(self.question.id)
        # generate result dictionary from search document
        result = document.to_dict()
        assert expected == result

    def test_variable_search_document_fields_missing_related_objects(self):
        self.question.instrument.analysis_unit = None
        self.question.instrument.period = None
        self.question.instrument.save()
        self.question.save()

        search = QuestionDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        expected = {"label": "Not Categorized", "label_de": "Nicht Kategorisiert"}
        assert expected == document.analysis_unit
        assert expected == document.period

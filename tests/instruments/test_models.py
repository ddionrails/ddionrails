# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for ddionrails.instruments.models """

import pytest

from ddionrails.instruments.models import ConceptQuestion
from tests.instruments.factories import QuestionFactory

pytestmark = [pytest.mark.instruments, pytest.mark.models]  # pylint: disable=invalid-name


class TestInstrumentModel:
    def test_string_method(self, instrument, study):
        assert str(instrument) == "/" + study.name + "/inst/" + instrument.name

    def test_get_absolute_url_method(self, instrument, study):
        assert (
            instrument.get_absolute_url() == "/" + study.name + "/inst/" + instrument.name
        )

    def test_layout_class_method(self, instrument):
        expected = "instrument"
        assert expected == instrument.layout_class()


class TestQuestionModel:
    def test_string_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert expected == str(question)

    def test_get_absolute_url_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert expected == question.get_absolute_url()

    def test_layout_class_method(self, question):
        expected = "question"
        assert expected == question.layout_class()

    def test_previous_question_method(self, question):
        previous_question = QuestionFactory(name="other-question", sort_id=1)
        question.sort_id = 2
        question.save()
        assert previous_question == question.previous_question()

    def test_previous_question_method_without_previous_question(self, question):
        expected = None
        assert expected == question.previous_question()

    def test_next_question_method(self, question):
        next_question = QuestionFactory(name="other-question", sort_id=2)
        assert next_question == question.next_question()

    def test_next_question_method_without_next_question(self, question):
        expected = None
        assert expected == question.next_question()

    def test_get_concepts_method_no_concept(self, question):
        """ Test Question.get_concepts() without concept-question-relation """
        result = question.get_concepts()
        expected = 0
        assert expected == result.count()

    def test_get_concepts_method_single_concept(self, question, concept):
        """ Test Question.get_concepts() with concept-question-relation"""

        # create a relation between question and concept
        ConceptQuestion.objects.create(concept=concept, question=question)
        result = question.get_concepts()
        expected = 1
        assert expected == result.count()
        assert concept == result.first()

    def test_get_cs_name_method(self):
        pass

    def test_title_method(self, question):
        assert question.title() == question.label

    def test_title_method_without_label(self, question):
        question.label = ""
        assert question.title() == question.name

    def test_translation_languages_method(self, question):
        question.items = [{"text_de": "German text"}]
        result = question.translation_languages()
        expected = ["de"]
        assert expected == result

    def test_translate_item_method(self):
        pass

    def test_translations_method(self):
        pass

    def test_item_array_method(self, question):
        question.items = [{"item": "Item", "scale": "Scale", "text": "Text"}]
        result = question.item_array()
        expected = [
            {
                "item": "Item",
                "scale": "Scale",
                "text": "Text",
                "sn": 0,
                "layout": "individual",
            }
        ]
        assert expected == result

    def test_comparison_string_method(self, question):
        question.items = [{"item": "Item", "scale": "Scale", "text": "Text"}]
        result = question.comparison_string()
        expected = ["Question: Some Question", "", "Item: Item (scale: Scale)", "Text"]
        assert expected == result

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for ddionrails.instruments.models """


import pytest

from ddionrails.instruments.models import ConceptQuestion
from tests.instruments.factories import QuestionFactory

pytestmark = [pytest.mark.instruments, pytest.mark.models]


@pytest.mark.django_db
def test_get_absolute_url_method(instrument, study):
    assert (
        instrument.get_absolute_url()
        == "/" + study.name + "/instruments/" + instrument.name
    )


class TestQuestionModel:
    def test_get_absolute_url_method(self, question):
        expected = (
            f"/{question.instrument.study.name}"
            f"/instruments/{question.instrument.name}"
            f"/{question.name}"
        )
        assert expected == question.get_absolute_url()

    def test_get_direct_url_method(self, question):
        expected = f"/question/{question.id}"
        assert expected == question.get_direct_url()

    def test_layout_class_method(self, question):
        expected = "question"
        assert expected == question.layout_class()

    def test_previous_question_method(self, question):
        previous_question = QuestionFactory(name="other-question", sort_id=1)
        question.sort_id = 2
        question.save()
        assert previous_question.name == question.previous_question()

    def test_previous_question_method_without_previous_question(self, question):
        expected = None
        assert expected == question.previous_question()

    def test_next_question_method(self, question):
        next_question = QuestionFactory(name="other-question", sort_id=2)
        assert next_question.name == question.next_question()

    def test_next_question_method_without_next_question(self, question):
        expected = None
        assert expected == question.next_question()

    def test_get_concepts_method_no_concept(self, question):
        """Test Question.get_concepts() without concept-question-relation"""
        result = question.get_concepts()
        expected = 0
        assert expected == result.count()

    def test_get_concepts_method_single_concept(self, question, concept):
        """Test Question.get_concepts() with concept-question-relation"""

        # create a relation between question and concept
        ConceptQuestion.objects.create(concept=concept, question=question)
        result = question.get_concepts()
        expected = 1
        assert expected == result.count()
        assert concept == result.first()

    def test_translation_languages_method(self, question):
        question.items = [{"text_de": "German text"}]
        result = question.translation_languages()
        expected = ["de"]
        assert expected == result

    def test_translate_item_method(self):
        pass

    def test_comparison_string_method(self, question):
        question.items = [{"item": "Item", "scale": "Scale", "text": "Text"}]
        result = question.comparison_string()
        expected = ["Question: Some Question", "", "Item: Item (scale: Scale)", "Text"]
        assert expected == result

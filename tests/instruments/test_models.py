# -*- coding: utf-8 -*-
""" Test cases for ddionrails.instruments.models """

import pytest

from ddionrails.instruments.models import ConceptQuestion

pytestmark = [pytest.mark.instrument, pytest.mark.models]


class TestInstrumentModel:
    def test_string_method(self, instrument, study):
        assert str(instrument) == "/" + study.name + "/inst/" + instrument.name

    def test_get_absolute_url_method(self, instrument, study):
        assert (
            instrument.get_absolute_url() == "/" + study.name + "/inst/" + instrument.name
        )


class TestQuestionModel:
    def test_string_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert str(question) == expected

    def test_get_absolute_url_method(self, question):
        expected = f"/{question.instrument.study.name}/inst/{question.instrument.name}/{question.name}"
        assert question.get_absolute_url() == expected

    def test_layout_class_method(self, question):
        expected = "question"
        assert question.layout_class() == expected

    def test_get_answers_method(self):
        pass

    def test_previous_question_method(self):
        pass

    def test_next_question_method(self):
        pass

    def test_get_concepts_method_no_concept(self, question):
        """ Test Question.get_concepts() without concept-question-relation """
        result = question.get_concepts()
        assert 0 == result.count()

    def test_get_concepts_method_single_concept(self, question, concept):
        """ Test Question.get_concepts() with concept-question-relation"""

        # create a relation between question and concept
        ConceptQuestion.objects.create(concept=concept, question=question)
        result = question.get_concepts()
        assert 1 == result.count()
        assert concept == result.first()

    def test_get_cs_name_method(self):
        pass

    def test_title_method(self, question):
        assert question.title() == question.label

    def test_title_method_without_label(self, question):
        question.label = ""
        assert question.title() == question.name

    def test_translation_languages_method(self):
        pass

    def test_translate_item_method(self):
        pass

    def test_translations_method(self):
        pass

    def test_item_array_method(self):
        pass

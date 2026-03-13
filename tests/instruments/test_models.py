# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for ddionrails.instruments.models"""

from django.test import TestCase

from ddionrails.instruments.models import ConceptQuestion
from tests.model_factories import (
    ConceptFactory,
    InstrumentFactory,
    QuestionFactory,
    StudyFactory,
)


class TestInstrumentAbsoluteURL(TestCase):

    def test_get_absolute_url_method(self):
        study = StudyFactory()
        instrument = InstrumentFactory(study=study)
        assert (
            instrument.get_absolute_url()
            == "/" + study.name + "/instruments/" + instrument.name
        )


class TestQuestionModel(TestCase):

    def setUp(self) -> None:
        self.question = QuestionFactory(sort_id=1)
        return super().setUp()

    def test_get_absolute_url_method(self):
        expected = (
            f"/{self.question.instrument.study.name}"
            f"/instruments/{self.question.instrument.name}"
            f"/{self.question.name}"
        )
        assert expected == self.question.get_absolute_url()

    def test_get_direct_url_method(self):
        expected = f"/question/{self.question.id}"
        assert expected == self.question.get_direct_url()

    def test_layout_class_method(self):
        expected = "question"
        assert expected == self.question.layout_class()

    def test_previous_question_method(self):
        previous_question = QuestionFactory(
            instrument=self.question.instrument, sort_id=1
        )
        self.question.sort_id = 2
        self.question.save()
        assert previous_question.name == self.question.previous_question()

    def test_previous_question_method_without_previous_question(self):
        expected = None
        assert expected == self.question.previous_question()

    def test_next_question_method(self):
        next_question = QuestionFactory(instrument=self.question.instrument, sort_id=2)
        assert next_question.name == self.question.next_question()

    def test_next_question_method_without_next_question(self):
        expected = None
        assert expected == self.question.next_question()

    def test_get_concepts_method_no_concept(self):
        """Test Question.get_concepts() without concept-question-relation"""
        result = self.question.get_concepts()
        expected = 0
        assert expected == result.count()

    def test_get_concepts_method_single_concept(self):
        """Test Question.get_concepts() with concept-question-relation"""

        concept = ConceptFactory(topics__study=self.question.instrument.study)

        # create a relation between question and concept
        ConceptQuestion.objects.create(concept=concept, question=self.question)
        result = self.question.get_concepts()
        expected = 1
        assert expected == result.count()
        assert concept == result.first()

    def test_translation_languages_method(self):
        self.question.items = [{"text_de": "German text"}]
        result = self.question.translation_languages()
        expected = ["de"]
        assert expected == result

    def test_translate_item_method(self):
        pass

    def test_comparison_string_method(self):
        self.question.items = [{"item": "Item", "scale": "Scale", "text": "Text"}]
        self.question.save()
        result = self.question.comparison_string()
        expected = [
            f"Question: {self.question.label}",
            "",
            "Item: Item (scale: Scale)",
            "Text",
        ]
        assert expected == result

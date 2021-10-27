# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for ddionrails.instruments.models """

import unittest
from io import BytesIO

import pytest
from django.core.files import File
from django.db import models
from filer.models import Folder, Image

from ddionrails.instruments.models import ConceptQuestion, Question, QuestionImage
from tests.instruments.factories import QuestionFactory

pytestmark = [pytest.mark.instruments, pytest.mark.models]


@pytest.mark.django_db
def test_get_absolute_url_method(instrument, study):
    assert instrument.get_absolute_url() == "/" + study.name + "/inst/" + instrument.name


class TestQuestionModel:
    def test_get_absolute_url_method(self, question):
        expected = (
            f"/{question.instrument.study.name}"
            f"/inst/{question.instrument.name}"
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


@pytest.mark.usefixtures("image_file", "question")
class TestQuestionImageModel(unittest.TestCase):

    image_file = BytesIO
    question = Question
    _filer_image = Image

    def test_save_with_question_object(self):
        django_file = File(self.image_file)

        _folder = self.create_folder_structure()
        self._filer_image, _ = Image.objects.get_or_create(
            folder=_folder, file=django_file
        )
        image = self.create_question_image()

        # Is the content in the correct type?
        self.assertIsInstance(image.image, Image)
        self.assertIsInstance(image.image, models.Model)
        # Was the object correctly inserted?
        self.assertIn(image, QuestionImage.objects.filter(id=image.id))

    def create_folder_structure(self):
        """Create folders and subfolders needed for the image storage."""
        _path = str(self.question).split("/")
        _path = [folder for folder in _path if folder]
        _parent, _ = Folder.objects.get_or_create(name=_path[0])
        for folder in _path[1:]:
            _parent, _ = Folder.objects.get_or_create(name=folder, parent=_parent)
        return _parent

    def create_question_image(self):
        """Create a QuestionImage object, that can be stored. """
        image = QuestionImage()
        image.image_id = self._filer_image.id
        image.question = self.question
        image.label = "test"
        image.language = "de"
        image.save()
        return image

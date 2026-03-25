# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.concepts app"""

from uuid import uuid4

from django.test import Client, TestCase
from django.urls import reverse

from ddionrails.instruments.models import Question
from tests import status
from tests.model_factories import ConceptFactory


class TestConceptDetailView(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client()
        cls.concept = ConceptFactory()
        return super().setUpClass()

    def test_detail_view_with_valid_id(self):
        valid_id = self.concept.id
        url = reverse("concepts:concept_detail", kwargs={"id": valid_id})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_detail_view_with_invalid_id(self):
        url = reverse("concepts:concept_detail", kwargs={"id": uuid4()})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_valid_name(self):
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": self.concept.name}
        )
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template_name = "concepts/concept_detail.html"
        assert template_name in (t.name for t in response.templates)

        expected_variables = list(self.concept.variables.all())
        output_variables = list(response.context["variables"])
        assert output_variables == expected_variables

        expected_questions = list(
            Question.objects.filter(concepts_questions__concept_id=self.concept.id).all()
        )
        output_questions = list(response.context["questions"])
        assert output_questions == expected_questions

    def test_detail_view_with_invalid_name(self):
        invalid_concept_name = "missing-concept"
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": invalid_concept_name}
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

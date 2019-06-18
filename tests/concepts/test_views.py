# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.concepts app """


import pytest
from django.urls import reverse

from ddionrails.instruments.models import Question
from tests import status

pytestmark = [pytest.mark.concepts, pytest.mark.views]


@pytest.mark.django_db
class TestConceptDetailView:
    def test_detail_view_with_valid_id(self, client, concept):
        valid_id = concept.id
        url = reverse("concepts:concept_detail", kwargs={"id": valid_id})
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_detail_view_with_invalid_id(self, client, uuid_identifier):
        url = reverse("concepts:concept_detail", kwargs={"id": uuid_identifier})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_valid_name(self, client, concept):
        concept_name = "some-concept"
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": concept_name}
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template_name = "concepts/concept_detail.html"
        assert template_name in (t.name for t in response.templates)

        expected_variables = list(concept.variables.all())
        output_variables = list(response.context["variables"])
        assert output_variables == expected_variables

        expected_questions = list(
            Question.objects.filter(concepts_questions__concept_id=concept.id).all()
        )
        output_questions = list(response.context["questions"])
        assert output_questions == expected_questions

    def test_detail_view_with_invalid_name(self, client):
        invalid_concept_name = "missing-concept"
        url = reverse(
            "concepts:concept_detail_name", kwargs={"concept_name": invalid_concept_name}
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

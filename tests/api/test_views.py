# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.api app """

import json
import unittest
from typing import Dict, List
from uuid import UUID

import pytest
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from ddionrails.api.views import BasketViewSet
from ddionrails.workspace.models import Basket, BasketVariable
from tests import status
from tests.data.factories import VariableFactory
from tests.factories import UserFactory

LANGUAGE = "en"

TEST_CASE = unittest.TestCase()


@pytest.fixture(name="variable_with_concept_and_topic")
def _variable_with_concept_and_topic(variable, concept, topic):
    """ A variable with a related concept and topic """
    concept.topics.add(topic)
    concept.save()
    variable.concept = concept
    variable.save()
    return variable, concept, topic


def response_is_json(response) -> bool:
    """ Helper function to validate a response's content type is JSON """
    expected_content_type = "application/json"
    return expected_content_type == response["content-type"]


class TestConceptByStudy:
    def test_json_response(self, study, client, concept, variable):
        variable.concept = concept
        variable.save()
        url = reverse(
            "api:concept_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept.name,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertTrue(response_is_json(response))

        response_dictionary = response.json()
        TEST_CASE.assertEqual(str(study.id), response_dictionary["study_id"])
        TEST_CASE.assertEqual(str(concept.id), response_dictionary["concept_id"])
        TEST_CASE.assertEqual(study.name, response_dictionary["study_name"])
        TEST_CASE.assertEqual(concept.name, response_dictionary["concept_name"])
        TEST_CASE.assertEqual(1, response_dictionary["variable_count"])
        TEST_CASE.assertEqual(
            variable.name, response_dictionary["variable_list"][0]["name"]
        )

    def test_json_response_without_variable_list(self, study, client, concept):
        url = reverse(
            "api:concept_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept.name,
            },
        )
        response = client.get(url, data={"variable_list": "false"})
        TEST_CASE.assertNotIn("variable_list", response.json())
        TEST_CASE.assertNotIn("question_list", response.json())

    def test_html_response_variable_html(self, study, client, concept, variable):
        variable.concept = concept
        variable.save()
        url = reverse(
            "api:concept_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept.name,
            },
        )
        response = client.get(url, data={"variable_html": "true"})
        expected_content_type = "text/html; charset=utf-8"
        TEST_CASE.assertEqual(expected_content_type, response["content-type"])
        TEST_CASE.assertEqual(LANGUAGE, response.context["language"])
        TEST_CASE.assertEqual(variable, response.context["variables"][0])

    def test_html_response_question_html(
        self, study, client, question_variable, concept_question
    ):
        # create a relation between variable - concept - question
        question_variable.variable.concept = concept_question.concept
        question_variable.variable.save()
        url = reverse(
            "api:concept_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept_question.concept.name,
            },
        )
        response = client.get(url, data={"question_html": "true"})
        expected_content_type = "text/html; charset=utf-8"
        TEST_CASE.assertEqual(expected_content_type, response["content-type"])
        TEST_CASE.assertEqual(LANGUAGE, response.context["language"])
        TEST_CASE.assertEqual([question_variable.question], response.context["questions"])


class TestTopicByStudy:
    def test_json_response(self, study, client, variable_with_concept_and_topic):
        _, _, topic = variable_with_concept_and_topic
        url = reverse(
            "api:topic_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertTrue(response_is_json(response))

        response_dictionary = response.json()
        TEST_CASE.assertEqual(str(study.id), response_dictionary["study_id"])
        TEST_CASE.assertEqual(str(topic.id), response_dictionary["topic_id"])
        TEST_CASE.assertEqual(study.name, response_dictionary["study_name"])
        TEST_CASE.assertEqual(topic.name, response_dictionary["topic_name"])
        TEST_CASE.assertEqual(1, response_dictionary["variable_count"])
        TEST_CASE.assertEqual([str(topic.id)], response_dictionary["topic_id_list"])

    def test_json_response_without_variable_list(
        self, study, client, variable_with_concept_and_topic
    ):
        _, _, topic = variable_with_concept_and_topic
        url = reverse(
            "api:topic_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
            },
        )
        response = client.get(url, data={"variable_list": "false"})
        TEST_CASE.assertNotIn("variable_list", response.json())
        TEST_CASE.assertNotIn("question_list", response.json())

    def test_html_response_variable_html(
        self, client, study, variable_with_concept_and_topic
    ):
        variable, _, topic = variable_with_concept_and_topic
        url = reverse(
            "api:topic_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
            },
        )
        response = client.get(url, data={"variable_html": "true"})
        expected_content_type = "text/html; charset=utf-8"
        TEST_CASE.assertEqual(expected_content_type, response["content-type"])
        TEST_CASE.assertEqual(LANGUAGE, response.context["language"])
        TEST_CASE.assertEqual(variable, response.context["variables"][0])

    def test_html_response_question_html(
        self, client, study, question_variable, variable_with_concept_and_topic
    ):
        _, _, topic = variable_with_concept_and_topic
        url = reverse(
            "api:topic_by_study",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
            },
        )
        response = client.get(url, data={"question_html": "true"})
        expected_content_type = "text/html; charset=utf-8"
        TEST_CASE.assertEqual(expected_content_type, response["content-type"])
        TEST_CASE.assertEqual(LANGUAGE, response.context["language"])
        TEST_CASE.assertEqual([question_variable.question], response.context["questions"])


class TestBasketsByStudyAndUser:
    def test_anonymous_user(self, client, study):
        url = reverse(
            "api:baskets_by_study_and_user",
            kwargs={"study_name": study.name, "language": LANGUAGE},
        )
        response = client.get(url)

        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertTrue(response_is_json(response))

        response_dictionary = response.json()
        expected = False
        TEST_CASE.assertIs(expected, response_dictionary["user_logged_in"])

        expected = []
        TEST_CASE.assertEqual(expected, response_dictionary["baskets"])

    def test_logged_in_user(self, client, study, basket):
        url = reverse(
            "api:baskets_by_study_and_user",
            kwargs={"study_name": study.name, "language": LANGUAGE},
        )
        client.force_login(user=basket.user)
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        response_dictionary = response.json()

        expected = True
        TEST_CASE.assertIs(expected, response_dictionary["user_logged_in"])
        expected = [basket.to_dict()]
        TEST_CASE.assertEqual(expected, response_dictionary["baskets"])


class TestAddVariablesByConceptView:
    def test_with_valid_name_and_id(  # pylint: disable=R0913
        self, study, client, basket, concept, variable
    ):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        variable.concept = concept
        variable.save()
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept.name,
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertEqual(1, BasketVariable.objects.count())
        basket_variable = BasketVariable.objects.first()
        TEST_CASE.assertEqual(variable, basket_variable.variable)
        TEST_CASE.assertEqual(basket, basket_variable.basket)

    def test_with_invalid_name(self, study, client, basket):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": "concept-not-in-db",
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())

    def test_with_invalid_id(self, study, client, concept):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "concept_name": concept.name,
                "basket_id": 1,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())


class TestAddVariablesByTopicView:
    def test_with_valid_name_and_id(
        self, study, client, basket, variable_with_concept_and_topic
    ):
        variable, _, topic = variable_with_concept_and_topic
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertEqual(1, BasketVariable.objects.count())
        basket_variable = BasketVariable.objects.first()
        TEST_CASE.assertEqual(variable, basket_variable.variable)
        TEST_CASE.assertEqual(basket, basket_variable.basket)

    def test_with_invalid_study_name(self, client, basket, topic):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": "study-not-in-db",
                "language": LANGUAGE,
                "topic_name": topic.name,
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())

    def test_with_invalid_topic_name(self, study, client, basket):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": "topic-not-in-db",
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())

    def test_with_invalid_id(self, study, client, topic):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "topic_name": topic.name,
                "basket_id": 1,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())


class TestAddVariableByIdView:
    def test_with_valid_ids(self, study, basket, variable, client):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "basket_id": basket.id,
                "variable_id": variable.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
        TEST_CASE.assertEqual(1, BasketVariable.objects.count())
        basket_variable = BasketVariable.objects.first()
        TEST_CASE.assertEqual(variable, basket_variable.variable)
        TEST_CASE.assertEqual(basket, basket_variable.basket)

    def test_with_invalid_basket_id(self, study, variable, client):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "basket_id": 1,
                "variable_id": variable.id,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())

    def test_with_invalid_variable_id(self, study, basket, client, uuid_identifier):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": LANGUAGE,
                "basket_id": basket.id,
                "variable_id": uuid_identifier,
            },
        )
        response = client.get(url)
        TEST_CASE.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())


@pytest.mark.parametrize(
    "language,expected",
    [("en", [{"title": "some-topic"}]), ("de", [{"title": "some-german-topic"}])],
)
def test_topic_list(client, topiclist, language, expected):
    url = reverse(
        "api:topic_list",
        kwargs={"study_name": topiclist.study.name, "language": language},
    )
    response = client.get(url)
    TEST_CASE.assertEqual(status.HTTP_200_OK, response.status_code)
    TEST_CASE.assertEqual(expected, response.json())
    response_is_json(response)


@pytest.mark.django_db
class TestBasketViewSet(unittest.TestCase):

    API_PATH = "/api/baskets/"
    variables: List[VariableFactory] = list()
    request_factory: APIRequestFactory

    def setUp(self):
        self.request_factory = APIRequestFactory()

        self._init_self_variables()

        self.study = self.variables[0].dataset.study
        self.user = UserFactory(username="test-user")

        self.basket = Basket()
        self.basket.name = "test-basket"
        self.basket.study = self.study
        self.basket.user = self.user
        self.basket.save()

        return super().setUp()

    def _init_self_variables(self):
        if self.variables:
            return None
        self.variables = list()
        for number in range(1, 100):
            self.variables.append(VariableFactory(name=f"{number}"))
        return None

    def test_get_basket(self):
        """Can we get the test basket from the API?"""
        results = self._get_api_GET_content()
        baskets_names = [result["name"] for result in results]

        self.assertIn(self.basket.name, baskets_names)

    def test_returned_fields(self):
        """Define fields that need to be present in API response."""
        results = self._get_api_GET_content()
        baskets_names = [result["name"] for result in results]
        test_basket = results[baskets_names.index(self.basket.name)]

        direct_fields = ["id", "name", "label", "description"]

        for field in direct_fields:
            self.assertIn(field, test_basket)
            self.assertEqual(getattr(self.basket, field), test_basket[field])

        self.assertIn("user_id", test_basket)
        self.assertEqual(self.basket.user.id, test_basket["user_id"])

        self.assertIn("study_id", test_basket)
        self.assertEqual(self.basket.study.id, UUID(test_basket["study_id"]))

    def test_create_basket(self):
        """Can we create a basket through the API?"""
        basket_data = {
            "user_id": self.user.id,
            "study_id": str(self.study.id),
            "name": "expected_basket",
            "label": "expected label",
            "description": "expected description",
        }
        client = APIClient()
        request = client.post(self.API_PATH, basket_data, format="json")
        # Only user with permisson should be able to create a basket
        # No User logged in:
        self.assertEqual(403, request.status_code)

        # Wrong user logged in:
        dummy_user = UserFactory(username="dummy")
        client.force_authenticate(user=dummy_user)
        request = client.post(self.API_PATH, basket_data, format="json")
        self.assertEqual(403, request.status_code)
        dummy_user.delete()

        # Correct user:
        client.force_authenticate(user=self.user)
        request = client.post(self.API_PATH, basket_data, format="json")

        baskets = self._get_api_GET_content()
        result = [basket for basket in baskets if basket["name"] == basket_data["name"]]
        self.assertEqual(1, len(result))

        result = result[0]
        for key, value in basket_data.items():
            self.assertEqual(value, result.get(key))

    def _get_api_GET_content(self) -> Dict[str, str]:
        request = self.request_factory.get(self.API_PATH, format="json")
        view = BasketViewSet.as_view({"get": "list"})
        force_authenticate(request, user=self.user)
        rendered_view = view(request).render()
        return json.loads(rendered_view.content).get("results")

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.api app """

import pytest
from django.urls import reverse

from ddionrails.workspace.models import BasketVariable
from tests import status

LANGUAGE = "en"


@pytest.fixture
def variable_with_concept_and_topic(variable, concept, topic):
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
        assert status.HTTP_200_OK == response.status_code
        assert response_is_json(response)

        response_dictionary = response.json()
        assert str(study.id) == response_dictionary["study_id"]
        assert str(concept.id) == response_dictionary["concept_id"]
        assert study.name == response_dictionary["study_name"]
        assert concept.name == response_dictionary["concept_name"]
        assert 1 == response_dictionary["variable_count"]
        assert variable.name == response_dictionary["variable_list"][0]["name"]

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
        assert "variable_list" not in response.json()
        assert "question_list" not in response.json()

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
        assert expected_content_type == response["content-type"]
        assert LANGUAGE == response.context["language"]
        assert variable == response.context["variables"][0]

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
        assert expected_content_type == response["content-type"]
        assert LANGUAGE == response.context["language"]
        assert [question_variable.question] == response.context["questions"]


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
        assert status.HTTP_200_OK == response.status_code
        assert response_is_json(response)

        response_dictionary = response.json()
        assert str(study.id) == response_dictionary["study_id"]
        assert str(topic.id) == response_dictionary["topic_id"]
        assert study.name == response_dictionary["study_name"]
        assert topic.name == response_dictionary["topic_name"]
        assert 1 == response_dictionary["variable_count"]
        assert [str(topic.id)] == response_dictionary["topic_id_list"]

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
        assert "variable_list" not in response.json()
        assert "question_list" not in response.json()

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
        assert expected_content_type == response["content-type"]
        assert LANGUAGE == response.context["language"]
        assert variable == response.context["variables"][0]

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
        assert expected_content_type == response["content-type"]
        assert LANGUAGE == response.context["language"]
        assert [question_variable.question] == response.context["questions"]


class TestBasketsByStudyAndUser:
    def test_anonymous_user(self, client, study):
        url = reverse(
            "api:baskets_by_study_and_user",
            kwargs={"study_name": study.name, "language": LANGUAGE},
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        assert response_is_json(response)
        response_dictionary = response.json()
        expected = False
        assert expected is response_dictionary["user_logged_in"]
        expected = []
        assert expected == response_dictionary["baskets"]

    def test_logged_in_user(self, client, study, basket):
        url = reverse(
            "api:baskets_by_study_and_user",
            kwargs={"study_name": study.name, "language": LANGUAGE},
        )
        client.force_login(user=basket.user)
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        response_dictionary = response.json()
        expected = True
        assert expected is response_dictionary["user_logged_in"]
        expected = [basket.to_dict()]
        assert expected == response_dictionary["baskets"]


class TestAddVariablesByConceptView:
    def test_with_valid_name_and_id(self, study, client, basket, concept, variable):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_200_OK == response.status_code
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert variable == basket_variable.variable
        assert basket == basket_variable.basket

    def test_with_invalid_name(self, study, client, basket):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_id(self, study, client, concept):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestAddVariablesByTopicView:
    def test_with_valid_name_and_id(
        self, study, client, basket, variable_with_concept_and_topic
    ):
        variable, _, topic = variable_with_concept_and_topic
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_200_OK == response.status_code
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert variable == basket_variable.variable
        assert basket == basket_variable.basket

    def test_with_invalid_study_name(self, client, basket, topic):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_topic_name(self, study, client, basket):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_id(self, study, client, topic):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestAddVariableByIdView:
    def test_with_valid_ids(self, study, basket, variable, client):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_200_OK == response.status_code
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert variable == basket_variable.variable
        assert basket == basket_variable.basket

    def test_with_invalid_basket_id(self, study, variable, client):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_variable_id(self, study, basket, client, uuid_identifier):
        assert 0 == BasketVariable.objects.count()
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
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


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
    assert status.HTTP_200_OK == response.status_code
    assert expected == response.json()
    response_is_json(response)

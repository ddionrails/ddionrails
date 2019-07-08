# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.api app """

import pytest
from django.urls import reverse

from ddionrails.workspace.models import BasketVariable
from tests import status


class TestPreviewView:
    def test_variable_preview(self, client, variable):
        url = f"/api/test/preview/variable/{variable.id}"
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    # TODO: Publication has a title field. This breaks the title() method call

    # def test_publication_preview(self, client, publication):
    #     url = f"/api/test/preview/publication/{publication.id}"
    #     response = client.get(url)
    #     assert status.HTTP_200_OK == response.status_code

    def test_question_preview(self, client, question):
        url = f"/api/test/preview/question/{question.id}"
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_concept_preview(self, client, concept):
        url = f"/api/test/preview/concept/{concept.id}"
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    @pytest.mark.django_db
    def test_preview_with_invalid_type(self, client, uuid_identifier):
        url = f"/api/test/preview/no-model/{uuid_identifier}"
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        content = response.content.decode("utf-8")
        expected = "No valid type."
        assert expected == content


class TestObjectRedirectView:
    def test_variable_redirect(self, client, variable):
        url = f"/api/test/redirect/variable/{variable.id}"
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_publication_redirect(self, client, publication):
        url = f"/api/test/redirect/publication/{publication.id}"
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_question_redirect(self, client, question):
        url = f"/api/test/redirect/question/{question.id}"
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_concept_redirect(self, client, concept):
        url = f"/api/test/redirect/concept/{concept.id}"
        response = client.get(url, follow=True)
        assert status.HTTP_200_OK == response.status_code
        assert response.redirect_chain[-1][0] == concept.get_absolute_url()

    @pytest.mark.django_db
    def test_redirect_to_home(self, client, uuid_identifier):
        url = f"/api/test/redirect/no-model/{uuid_identifier}"
        response = client.get(url, follow=True)
        assert status.HTTP_200_OK == response.status_code
        expected = "/"
        assert expected == response.redirect_chain[-1][0]


class TestAddVariablesByConceptView:
    def test_with_valid_name_and_id(self, study, client, basket, concept, variable):
        assert 0 == BasketVariable.objects.count()
        variable.concept = concept
        variable.save()
        language = "en"
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": language,
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

    def test_with_invalid_name(self, study, client, basket, variable):
        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": language,
                "concept_name": "concept-not-in-db",
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_id(self, study, client, concept):
        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variables_by_concept",
            kwargs={
                "study_name": study.name,
                "language": language,
                "concept_name": concept.name,
                "basket_id": 1,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestAddVariablesByTopicView:
    def test_with_valid_name_and_id(
        self, study, client, basket, topic, concept, variable
    ):
        # set up relations topic -> concept -> variable
        concept.topics.add(topic)
        concept.save()
        variable.concept = concept
        variable.save()

        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": language,
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
        language = "en"
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": "study-not-in-db",
                "language": language,
                "topic_name": topic.name,
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_topic_name(self, study, client, basket, topic):
        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": language,
                "topic_name": "topic-not-in-db",
                "basket_id": basket.id,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_id(self, study, client, topic):
        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variables_by_topic",
            kwargs={
                "study_name": study.name,
                "language": language,
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
        language = "en"
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": language,
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
        language = "en"
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": language,
                "basket_id": 1,
                "variable_id": variable.id,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_variable_id(self, study, basket, client, uuid_identifier):
        assert 0 == BasketVariable.objects.count()
        language = "en"
        url = reverse(
            "api:add_variable_by_id",
            kwargs={
                "study_name": study.name,
                "language": language,
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
    expected_content_type = "application/json"
    assert expected_content_type == response["content-type"]

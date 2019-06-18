# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.api app """

import pytest
from django.urls import reverse

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

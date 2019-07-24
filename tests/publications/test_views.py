# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.publications app """

import pytest
from django.urls import reverse

from tests import status


class TestPublicationRedirectView:
    def test_with_valid_id(self, client, publication):
        url = reverse("publication_redirect", kwargs={"id": publication.id})
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    @pytest.mark.django_db
    def test_with_invalid_id(self, client, uuid_identifier):
        url = reverse("publication_redirect", kwargs={"id": uuid_identifier})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestPublicationDetailView:
    def test_detail_view_with_existing_names(self, client, publication):
        url = reverse(
            "publ:publication_detail",
            kwargs={
                "study_name": publication.study.name,
                "publication_name": publication.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_detail_view_with_invalid_study_name(self, client, publication):
        url = reverse(
            "publ:publication_detail",
            kwargs={
                "study_name": "invalid-study-name",
                "publication_name": publication.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestStudyPublicationList:
    def test_with_valid_name(self, client, publication):
        url = reverse(
            "publ:study_publication_list", kwargs={"study_name": publication.study.name}
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        assert publication.study == response.context["study"]

    @pytest.mark.django_db
    def test_with_invalid_name(self, client):
        url = reverse(
            "publ:study_publication_list", kwargs={"study_name": "study-not-in-db"}
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

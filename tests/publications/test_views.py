# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.publications app"""

from uuid import uuid1

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ddionrails.publications.models import Publication
from tests import status
from tests.model_factories import PublicationFactory


class TestPublicationRedirectView(TestCase):

    publication: Publication
    cleint: Client

    def setUp(self) -> None:
        self.publication = PublicationFactory()
        self.client = Client()
        return super().setUp()

    def test_with_valid_id(self):
        url = reverse("publication_redirect", kwargs={"id": self.publication.id})
        response = self.client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_with_invalid_id(self):
        url = reverse("publication_redirect", kwargs={"id": uuid1()})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestPublicationDetailView(TestCase):

    publication: Publication
    cleint: Client

    def setUp(self) -> None:
        self.publication = PublicationFactory()
        self.client = Client()
        return super().setUp()

    def test_detail_view_with_existing_names(self):
        url = reverse(
            "publ:publication_detail",
            kwargs={
                "study_name": self.publication.study.name,
                "publication_name": self.publication.name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_detail_view_with_invalid_study_name(self):
        url = reverse(
            "publ:publication_detail",
            kwargs={
                "study_name": "invalid-study-name",
                "publication_name": self.publication.name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestStudyPublicationList(TestCase):

    publication: Publication
    cleint: Client

    def setUp(self) -> None:
        self.publication = PublicationFactory()
        self.client = Client()
        return super().setUp()

    def test_with_valid_name(self):
        url = reverse(
            "publ:study_publication_list",
            kwargs={"study_name": self.publication.study.name},
        )
        response = self.client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_with_invalid_name(self):
        url = reverse(
            "publ:study_publication_list", kwargs={"study_name": "study-not-in-db"}
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

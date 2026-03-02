# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.studies app"""

import pytest
from django.test import Client, TestCase
from django.urls import reverse

from tests import status
from tests.model_factories import StudyFactory

pytestmark = [pytest.mark.studies, pytest.mark.views]

LANGUAGE = "en"


class TestStudyAndTopicDetailView(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.client = Client()
        return super().setUp()

    def test_study_detail_view_with_existing_study_pk(self):
        url = reverse("study_detail", kwargs={"study_name": self.study.name})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "studies/study_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["study"] == self.study

    def test_study_detail_view_with_non_existing_study_name(self):
        non_existing_study_name = "not-in-database"
        url = reverse("study_detail", kwargs={"study_name": non_existing_study_name})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_study_topics_view_with_existing_study_name(self):
        url = reverse("study_topics", kwargs={"study_name": self.study.name})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_study_topics_view_with_non_existing_study_name(self):
        non_existing_study_name = "not-in-database"
        url = reverse(
            "study_topics",
            kwargs={"study_name": non_existing_study_name},
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

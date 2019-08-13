# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.studies app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.studies, pytest.mark.views]

LANGUAGE = "en"


class TestStudyDetailView:
    def test_study_detail_view_with_existing_study_pk(self, client, study):
        url = reverse("study_detail", kwargs={"study_name": study.name})
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "studies/study_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["study"] == study
        expected_datasets = list(study.datasets.all())
        output_datasets = list(response.context["dataset_list"])
        assert expected_datasets == output_datasets
        expected_instruments = list(study.instruments.all())
        output_instruments = list(response.context["instrument_list"])
        assert expected_instruments == output_instruments

    @pytest.mark.django_db
    def test_study_detail_view_with_non_existing_study_name(self, client):
        non_existing_study_name = "not-in-database"
        url = reverse("study_detail", kwargs={"study_name": non_existing_study_name})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestStudyTopicsView:
    def test_study_topics_view_with_existing_study_name(self, client, study):
        url = reverse(
            "study_topics", kwargs={"study_name": study.name, "language": LANGUAGE}
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    @pytest.mark.django_db
    def test_study_topics_view_with_non_existing_study_name(self, client):
        non_existing_study_name = "not-in-database"
        url = reverse(
            "study_topics",
            kwargs={"study_name": non_existing_study_name, "language": LANGUAGE},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

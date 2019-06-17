# -*- coding: utf-8 -*-

""" Test cases for ModelAdmins in ddionrails.concepts app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


def test_analyis_unit_admin_list(admin_client, analysis_unit):
    """ Test the AnalysisUnitAdmin changelist """
    url = reverse("admin:concepts_analysisunit_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_analyis_unit_admin_detail(admin_client, analysis_unit):
    """ Test the AnalysisUnitAdmin change_view """
    url = reverse("admin:concepts_analysisunit_change", args=(analysis_unit.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_concept_admin_list(admin_client, concept):
    """ Test the ConceptAdmin changelist """
    url = reverse("admin:concepts_concept_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_concept_admin_detail(admin_client, concept):
    """ Test the ConceptAdmin change_view """
    url = reverse("admin:concepts_concept_change", args=(concept.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_conceptual_dataset_admin_list(admin_client, conceptual_dataset):
    """ Test the ConceptualDatasetAdmin changelist """
    url = reverse("admin:concepts_conceptualdataset_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_conceptual_dataset_admin_detail(admin_client, conceptual_dataset):
    """ Test the ConceptualDatasetAdmin change_view """
    url = reverse(
        "admin:concepts_conceptualdataset_change", args=(conceptual_dataset.id,)
    )
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_period_admin_list(admin_client, period):
    """ Test the PeriodAdmin changelist """
    url = reverse("admin:concepts_period_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_period_admin_detail(admin_client, period):
    """ Test the PeriodAdmin change_view """
    url = reverse("admin:concepts_period_change", args=(period.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_topic_admin_list(admin_client, topic):
    """ Test the TopicAdmin changelist """
    url = reverse("admin:concepts_topic_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_topic_admin_detail(admin_client, topic):
    """ Test the TopicAdmin change_view """
    url = reverse("admin:concepts_topic_change", args=(topic.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

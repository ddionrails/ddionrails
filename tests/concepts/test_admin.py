import pytest
from tests import status

pytestmark = [pytest.mark.django_db]

def test_analyis_unit_admin(admin_client, analysis_unit):
    url = "/admin/concepts/analysisunit/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

def test_concept_admin(admin_client, concept):
    url = "/admin/concepts/concept/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

def test_conceptual_dataset_admin(admin_client, conceptual_dataset):
    url = "/admin/concepts/conceptualdataset/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

def test_period_admin(admin_client, period):
    url = "/admin/concepts/period/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code
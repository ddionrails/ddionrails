import pytest
from tests import status

pytestmark = [pytest.mark.django_db]

def test_dataset_admin(admin_client, dataset):
    url = "/admin/data/dataset/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

def test_variable_admin(admin_client, variable):
    url = "/admin/data/variable/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

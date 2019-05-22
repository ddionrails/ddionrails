import pytest

from tests import status

pytestmark = [pytest.mark.django_db]


def test_basket_variable_admin(admin_client, basket_variable):
    url = "/admin/workspace/basketvariable/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_basket_admin(admin_client, basket):
    url = "/admin/workspace/basket/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_script_admin(admin_client, script):
    url = "/admin/workspace/script/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

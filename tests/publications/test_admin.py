import pytest

from tests import status

pytestmark = [pytest.mark.django_db]


def test_attachment_admin(admin_client, attachment):
    url = "/admin/publications/attachment/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_publication_admin(admin_client, publication):
    url = "/admin/publications/publication/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

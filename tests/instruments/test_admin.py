import pytest
from tests import status

pytestmark = [pytest.mark.django_db]

def test_instrument_admin(admin_client, instrument):
    url = "/admin/instruments/instrument/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

def test_question_admin(admin_client, question):
    url = "/admin/instruments/question/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

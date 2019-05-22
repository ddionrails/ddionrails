import pytest
from tests import status

pytestmark = [pytest.mark.django_db]

def test_study_admin(admin_client, study):
    url = "/admin/studies/study/"
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

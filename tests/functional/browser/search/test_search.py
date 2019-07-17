import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.concepts, pytest.mark.views]


@pytest.mark.django_db
def test_search_url(client):
    url = reverse("search")
    response = client.get(url)
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_concepts_url(client):
    response = client.get("/search/concepts")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_publications_url(client):
    response = client.get("/search/publications")
    assert status.HTTP_200_OK == response.status_code

import pytest

from tests import status

pytestmark = [pytest.mark.concepts, pytest.mark.views]


@pytest.mark.django_db
def test_search_url(client):
    response = client.get("/search/")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_all_url(client):
    response = client.get("/search/all")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_concepts_url(client):
    response = client.get("/search/concepts")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_publications_url(client):
    response = client.get("/search/publications")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_questions_url(client):
    response = client.get("/search/questions")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_topics_url(client):
    response = client.get("/search/topics")
    assert status.HTTP_200_OK == response.status_code


@pytest.mark.django_db
def test_search_variables_url(client):
    response = client.get("/search/variables")
    assert status.HTTP_200_OK == response.status_code

import pytest

from elastic.views import search, angular
from django.urls import reverse, resolve


pytestmark = [pytest.mark.elastic, pytest.mark.views]

class TestSearchView:
    def test_search_view(self, client, study):
        url = reverse("elastic:search")
        response = client.get(url)
        assert response.status_code == 200


class TestAngularView:
    pass


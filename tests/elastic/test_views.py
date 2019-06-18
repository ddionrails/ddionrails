# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.elastic app """

import pytest
from django.urls import reverse

pytestmark = [pytest.mark.elastic, pytest.mark.views]  # pylint: disable=invalid-name


class TestSearchView:
    def test_search_view(self, client, study):
        url = reverse("elastic:search")
        response = client.get(url)
        assert response.status_code == 200

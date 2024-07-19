# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.config app """

import unittest
from datetime import datetime
from typing import Dict, List

import pytest
from django.urls import reverse

from config.views import (
    HomePageView,
    bad_request,
    page_not_found,
    permission_denied,
    server_error,
)
from ddionrails.base.models import News
from tests import status

pytestmark = [pytest.mark.django_db]


class TestPageViews:
    def test_contact_page(self, client):
        url = reverse("contact")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        content = str(response.content)
        assert "Contact / feedback" in content
        assert "SOEP Community Management" in content
        assert "GitHub" in content

    def test_home_page(self, client):
        url = reverse("home")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_imprint_page(self, client):
        url = reverse("imprint")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        content = str(response.content)
        assert "Imprint" in content
        assert "Privacy policy at DIW Berlin" in content


@pytest.mark.usefixtures("news")
class TestViewFunctions(unittest.TestCase):
    news: News = News()
    news_bullets: List[str] = []

    def test_news(self):
        news_date: datetime = self.news.date
        news_data: Dict[str, str] = {}
        news_data["news_month"] = news_date.strftime("%B")
        news_data["news_year"] = news_date.strftime("%Y")
        news_html = str(HomePageView().news)
        for date_content in news_data.values():
            self.assertIn(date_content, news_html)

        for point in self.news_bullets:
            self.assertIn(point, news_html)


class TestErrorTemplates:
    url = reverse("home")

    def test_400_template(self, rf):
        request = rf.get(self.url)
        response = bad_request(request, exception="")
        assert status.HTTP_400_BAD_REQUEST == response.status_code
        assert "Bad Request (400)" in str(response.content)

    def test_403_template(self, rf):
        request = rf.get(self.url)
        response = permission_denied(request, exception="")
        assert status.HTTP_403_FORBIDDEN == response.status_code
        assert "Forbidden (403)" in str(response.content)

    def test_404_template(self, rf):
        request = rf.get(self.url)
        response = page_not_found(request, exception="")
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert "Page not found (404)" in str(response.content)

    def test_500_template(self, rf):
        request = rf.get(self.url)
        response = server_error(request)
        assert status.HTTP_500_INTERNAL_SERVER_ERROR == response.status_code
        assert "Internal Server Error (500)" in str(response.content)

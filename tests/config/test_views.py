# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.config app"""

from datetime import datetime
from typing import Dict, List

from django.test import LiveServerTestCase, TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from markdown import markdown

from config.views import (
    HomePageView,
    bad_request,
    page_not_found,
    permission_denied,
    server_error,
)
from ddionrails.base.models import News
from tests import status
from tests.model_factories import NewsFactory


class TestPageViews(LiveServerTestCase):
    def test_contact_page(self):
        url = reverse("contact")
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        content = str(response.content)
        self.assertIn("Contact / feedback", content)
        self.assertIn("SOEP Community Management", content)
        self.assertIn("GitHub", content)

    def test_home_page(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @override_settings(INSTITUTE_NAME="TEST")
    def test_imprint_page(self):
        url = f"{self.live_server_url}/imprint/"
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        content = str(response.content)
        self.assertIn("Imprint", content)
        self.assertIn("Privacy policy at TEST", content)


class TestViewFunctions(TestCase):
    news: News = News()
    news_bullets: List[str] = []

    def test_news(self):
        news = NewsFactory()
        news_date: datetime = news.date
        news_data: Dict[str, str] = {}
        news_data["news_month"] = news_date.strftime("%B")
        news_data["news_year"] = news_date.strftime("%Y")
        news_html = HomePageView().news
        content = markdown(news.content, extension=["nl2br"])
        content_de = markdown(news.content_de, extension=["nl2br"])
        self.assertIn(content, news_html["en"])
        self.assertIn(content_de, news_html["de"])


class TestErrorTemplates(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.rf = RequestFactory()
        cls.url = reverse("home")
        return super().setUpClass()

    def test_400_template(self):
        request = self.rf.get(self.url)
        response = bad_request(request, exception="")
        assert status.HTTP_400_BAD_REQUEST == response.status_code
        assert "Bad Request (400)" in str(response.content)

    def test_403_template(self):
        request = self.rf.get(self.url)
        response = permission_denied(request, exception="")
        assert status.HTTP_403_FORBIDDEN == response.status_code
        assert "Forbidden (403)" in str(response.content)

    def test_404_template(self):
        request = self.rf.get(self.url)
        response = page_not_found(request, exception="")
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert "Page not found (404)" in str(response.content)

    def test_500_template(self):
        request = self.rf.get(self.url)
        response = server_error(request)
        assert status.HTTP_500_INTERNAL_SERVER_ERROR == response.status_code
        assert "Internal Server Error (500)" in str(response.content)

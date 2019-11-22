# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for models in ddionrails.base app """

import unittest
from datetime import datetime

import pytest
from dateutil import tz

from ddionrails.base.models import News, Singleton, System

pytestmark = [pytest.mark.ddionrails, pytest.mark.models]  # pylint: disable=invalid-name


class TestSystemModel:
    def test_repo_url_method(self, system, settings):
        assert system.repo_url() + settings.SYSTEM_REPO_URL

    def test_get_method(self, system):  # pylint: disable=unused-argument
        result = System.get()
        assert isinstance(result, System)

    @pytest.mark.django_db
    def test_get_method_with_creation(
        self,
    ):  # pylint: disable=unused-argument,invalid-name
        result = System.get()
        assert isinstance(result, System)


class TestNewsModel(unittest.TestCase):
    def test_news_ancestry(self):
        self.assertIsInstance(News(), Singleton)

    @pytest.mark.django_db
    def test_news_date(self):
        _news = News.objects.create()
        _news.content = ""
        _news.save()
        timedelta = datetime.now(tz=tz.gettz("UTC")) - _news.date
        self.assertAlmostEqual(timedelta.seconds, 0, delta=1)

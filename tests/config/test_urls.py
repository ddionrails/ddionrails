# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name,C0415

"""Test cases for Root URLConf of ddionrails project"""

from importlib import reload
from typing import List

from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.urls import resolve, reverse
from django.urls.base import clear_url_caches

import config.urls


class TestUrlPatternsPresent(LiveServerTestCase):

    def _django_debug_toolbar_found(self, urlpatterns: List) -> bool:
        """Returns True if an urlpattern has "djdt" as its app_name"""
        for pattern in urlpatterns:
            try:
                if pattern.app_name == "djdt":
                    return True
            except AttributeError:
                pass
        return False

    def _media_pattern_found(self, urlpatterns) -> bool:
        """Returns True if an urlpattern startswith "^media/" """
        for pattern in urlpatterns:
            if str(pattern.pattern).startswith("^media/"):
                return True
        return False

    @override_settings(DEBUG=True)
    def test_urlconf_with_debug_true(self):
        clear_url_caches()
        reload(config.urls)

        assert self._django_debug_toolbar_found(config.urls.urlpatterns) is True
        assert self._media_pattern_found(config.urls.urlpatterns) is True

    @override_settings(DEBUG=False)
    def test_urlconf_with_debug_false(self):
        clear_url_caches()
        reload(config.urls)

        assert self._django_debug_toolbar_found(config.urls.urlpatterns) is False
        assert self._media_pattern_found(config.urls.urlpatterns) is False

    def test_imprint(self):
        assert "/imprint/" == reverse("imprint")
        assert "imprint" == resolve("/imprint/").view_name

    def test_search(self):
        assert "/search/" == reverse("search")
        assert "search-redirect" == resolve("/search/").view_name

    def test_search_concepts(self):
        assert "search" == resolve("/search/concepts").view_name

    def test_search_topics(self):
        assert "search" == resolve("/search/topics").view_name

    def test_search_publications(self):
        assert "search" == resolve("/search/publications").view_name

    def test_search_questions(self):
        assert "search" == resolve("/search/questions").view_name

    def test_search_variables(self):
        assert "search" == resolve("/search/variables").view_name

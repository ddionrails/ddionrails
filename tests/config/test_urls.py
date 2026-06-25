# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name,C0415

"""Test cases for Root URLConf of ddionrails project"""

from django.test import LiveServerTestCase
from django.urls import resolve, reverse


class TestUrlPatternsPresent(LiveServerTestCase):

    def _media_pattern_found(self, urlpatterns) -> bool:
        """Returns True if an urlpattern startswith "^media/" """
        for pattern in urlpatterns:
            if str(pattern.pattern).startswith("^media/"):
                return True
        return False

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

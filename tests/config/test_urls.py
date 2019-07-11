# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

""" Test cases for Root URLConf of ddionrails project """

from importlib import reload
from typing import List

from django.urls import resolve, reverse
from django.urls.base import clear_url_caches

import config.urls


def django_debug_toolbar_found(urlpatterns: List) -> bool:
    """ Returns True if an urlpattern has "djdt" as its app_name """
    for pattern in urlpatterns:
        try:
            if pattern.app_name == "djdt":
                return True
        except AttributeError:
            pass
    return False


def media_pattern_found(urlpatterns: List) -> bool:
    """ Returns True if an urlpattern startswith "^media/" """
    for pattern in urlpatterns:
        if str(pattern.pattern).startswith("^media/"):
            return True
    return False


def test_urlconf_with_debug_true(settings):
    settings.DEBUG = True
    clear_url_caches()
    reload(config.urls)
    from config.urls import urlpatterns

    assert django_debug_toolbar_found(urlpatterns) is True
    assert media_pattern_found(urlpatterns) is True


def test_urlconf_with_debug_false(settings):
    settings.DEBUG = False
    clear_url_caches()
    reload(config.urls)
    from config.urls import urlpatterns

    assert django_debug_toolbar_found(urlpatterns) is False
    assert media_pattern_found(urlpatterns) is False


def test_imprint():
    assert "/imprint/" == reverse("imprint")
    assert "imprint" == resolve("/imprint/").view_name


def test_search():
    assert "/search/" == reverse("search")
    assert "search" == resolve("/search/").view_name


def test_search_concepts():
    assert "search" == resolve("/search/concepts").view_name


def test_search_topics():
    assert "search" == resolve("/search/topics").view_name


def test_search_publications():
    assert "search" == resolve("/search/publications").view_name


def test_search_questions():
    assert "search" == resolve("/search/questions").view_name


def test_search_variables():
    assert "search" == resolve("/search/variables").view_name

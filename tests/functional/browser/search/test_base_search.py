# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from urllib.parse import urljoin

import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


def test_base_search(
    browser, live_server, search_test_case
):  # pylint: disable=unused-argument
    base_search_url = urljoin(live_server.url, "search/")
    browser.visit(base_search_url)
    heading = browser.find_by_tag("h1").first.text
    expected = "Search"
    assert expected == heading
    expected = "Search | paneldata.org"
    assert expected == browser.title


@pytest.mark.skip
def test_concepts_search(
    browser, live_server, search_test_case  # pylint: disable=unused-argument
):

    concepts_search_url = urljoin(live_server.url, "search/concepts")
    browser.visit(concepts_search_url)


@pytest.mark.skip
def test_topics_search(
    browser, live_server, search_test_case  # pylint: disable=unused-argument
):

    topics_search_url = urljoin(live_server.url, "search/topics")
    browser.visit(topics_search_url)


@pytest.mark.skip
def test_variables_search(
    browser, live_server, search_test_case  # pylint: disable=unused-argument
):

    variables_search_url = urljoin(live_server.url, "search/variables")
    browser.visit(variables_search_url)


@pytest.mark.skip
def test_questions_search(
    browser, live_server, search_test_case  # pylint: disable=unused-argument
):

    questions_search_url = urljoin(live_server.url, "search/questions")
    browser.visit(questions_search_url)

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

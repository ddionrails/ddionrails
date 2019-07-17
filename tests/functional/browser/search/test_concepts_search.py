# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from urllib.parse import urlencode, urljoin

import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


@pytest.fixture
def concepts_search_url(live_server):
    return urljoin(live_server.url, "search/concepts")


def test_concepts_search_is_accessible(
    browser,
    concepts_search_url,
    search_test_case,
    concept,  # pylint: disable=unused-argument
):
    browser.visit(concepts_search_url)
    assert browser.is_text_present("Concepts")
    assert browser.is_text_present(concept.label, wait_time=1)


def test_concepts_search_by_label_de(
    browser,
    concepts_search_url,
    search_test_case,
    concept,  # pylint: disable=unused-argument
):
    concept.name = "pzuf01"
    concept.label = "satisfaction with health"
    concept.label_de = "zufriedenheit gesundheit"
    concept.save()

    query = urlencode({"Search": f'"{concept.label_de}"'})
    url = f"{concepts_search_url}?{query}"
    browser.visit(url)
    assert browser.is_text_present("Concepts")
    assert browser.is_text_present(concept.label, wait_time=1)

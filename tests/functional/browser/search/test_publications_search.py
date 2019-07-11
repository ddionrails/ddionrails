# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from urllib.parse import urlencode, urljoin

import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]

# browser.screenshot("/usr/src/app/local/your_screenshot-search", full=True)


@pytest.fixture
def publications_search_url(live_server):
    return urljoin(live_server.url, "search/publications")


def test_publications_search_is_accessible(
    browser, publications_search_url, search_test_case  # pylint: disable=unused-argument
):
    browser.visit(publications_search_url)
    assert browser.is_text_present("Publications")
    title = "Some publication with Umlauts"
    browser.find_by_id("Search-input").fill(title)
    assert browser.is_text_present(title, wait_time=1)


def test_publications_search_study_facet_url_parameters(
    browser, publications_search_url, search_test_case  # pylint: disable=unused-argument
):
    """ Test that http://localhost/search/publications?Studies=["Some Study"] is accessible
        and displays the publication
    """
    query = urlencode({"Studies": '["Some Study"]'})
    url = f"{publications_search_url}?{query}"
    browser.visit(url)
    browser.screenshot("/usr/src/app/local/your_screenshot-search2", full=True)
    title = "Some publication with Umlauts"
    assert browser.is_text_present(title, wait_time=1)


def test_publications_search_type_facet_url_parameters(
    browser, publications_search_url, search_test_case  # pylint: disable=unused-argument
):
    """ Test that http://localhost/search/publications?Types=["book"] is accessible
        and displays the publication
    """
    query = urlencode({"Types": '["book"]'})
    url = f"{publications_search_url}?{query}"
    browser.visit(url)
    title = "Some publication with Umlauts"
    assert browser.is_text_present(title, wait_time=1)


def test_publications_search_year_facet_url_parameters(
    browser, publications_search_url, search_test_case  # pylint: disable=unused-argument
):
    """ Test that http://localhost/search/publications?Years=["2019"] is accessible
        and displays the publication
    """
    query = urlencode({"Years": '["2019"]'})
    url = f"{publications_search_url}?{query}"
    browser.visit(url)
    title = "Some publication with Umlauts"
    assert browser.is_text_present(title, wait_time=1)

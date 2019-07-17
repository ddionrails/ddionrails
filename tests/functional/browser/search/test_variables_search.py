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
def variables_search_url(live_server):
    return urljoin(live_server.url, "search/variables")


def test_variables_search_is_accessible(
    browser,
    variables_search_url,
    search_test_case,
    variable,  # pylint: disable=unused-argument
):
    browser.visit(variables_search_url)
    assert browser.is_text_present("Variables")
    assert browser.is_text_present(variable.label, wait_time=1)


def test_variables_search_by_label_de(
    browser,
    variables_search_url,
    search_test_case,
    variable,  # pylint: disable=unused-argument
):
    variable.name = "ple0081"
    variable.label = "Currently Smoke"
    variable.label_de = "Rauchen gegenwaertig"
    variable.save()

    # search with "ae"
    query = urlencode({"Search": f'"{variable.label_de}"'})
    url = f"{variables_search_url}?{query}"
    browser.visit(url)
    assert browser.is_text_present("Variables")
    assert browser.is_text_present(variable.label, wait_time=1)

    # search with "ä"
    query = urlencode({"Search": "Rauchen gegenwärtig"})
    url = f"{variables_search_url}?{query}"
    browser.visit(url)
    assert browser.is_text_present("Variables")
    assert browser.is_text_present(variable.label, wait_time=1)

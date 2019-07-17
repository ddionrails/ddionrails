# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from urllib.parse import urljoin

import pytest

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


@pytest.fixture
def topics_search_url(live_server):
    return urljoin(live_server.url, "search/topics")


def test_questions_search_is_accessible(
    browser, topics_search_url, search_test_case, topic  # pylint: disable=unused-argument
):
    browser.visit(topics_search_url)
    assert browser.is_text_present("Topics")
    assert browser.is_text_present(topic.label, wait_time=1)

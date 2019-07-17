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
def questions_search_url(live_server):
    return urljoin(live_server.url, "search/questions")


def test_questions_search_is_accessible(
    browser,
    questions_search_url,
    search_test_case,
    question,  # pylint: disable=unused-argument
):
    browser.visit(questions_search_url)
    assert browser.is_text_present("Questions")
    assert browser.is_text_present(question.label, wait_time=1)

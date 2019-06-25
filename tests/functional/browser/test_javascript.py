# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Functional test cases for Javascript interaction with the ddionrails project """

import pytest

pytestmark = [
    pytest.mark.functional,
    pytest.mark.django_db,
]  # pylint: disable=invalid-name


def test_studies_dropdown_menu(
    browser, live_server, study
):  # pylint: disable=unused-argument
    browser.visit(live_server.url)
    studies_dropdown_menu = browser.find_by_xpath(
        '//button[contains(text(), "Studies")]'
    ).first
    aria_expanded = studies_dropdown_menu["aria-expanded"]
    assert aria_expanded == "false"
    studies_dropdown_menu.click()
    aria_expanded = studies_dropdown_menu["aria-expanded"]
    assert aria_expanded == "true"
    browser.find_by_id("nav-container").first.find_by_xpath("//ul/li/a").first.click()

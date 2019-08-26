# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Functional test cases for browser interaction with the ddionrails project """


import pytest

pytestmark = [
    pytest.mark.functional,
    pytest.mark.django_db,
]  # pylint: disable=invalid-name


def test_get_contact_page_from_home(browser, live_server):
    expected = "Contact / feedback"
    browser.visit(live_server.url)
    browser.find_link_by_text("Contact / feedback").first.click()
    headers = browser.find_by_tag("h1")
    assert expected in (header.text for header in headers)


def test_get_imprint_page_from_home(browser, live_server):
    expected = "Imprint"
    browser.visit(live_server.url)
    browser.find_link_by_text("Imprint").first.click()
    headers = browser.find_by_tag("h1")
    assert expected in (header.text for header in headers)


def test_get_login_page_from_home(browser, live_server):
    browser.visit(live_server.url)
    browser.find_link_by_text("Register / log in").first.click()
    assert "User login" in browser.html


def test_get_back_home_from_other_page(browser, search_url):
    browser.visit(search_url)
    browser.find_link_by_text("paneldata.org").first.click()
    expected = "Home | paneldata.org"
    assert expected == browser.title


def test_get_register_page_from_login(browser, login_url):
    browser.visit(login_url)
    browser.find_link_by_partial_href("register").first.click()
    assert "User registration" in browser.html


def test_get_password_reset_page_from_login(browser, login_url):
    expected = "Django administration"
    browser.visit(login_url)
    browser.find_link_by_partial_href("password_reset").first.click()
    headers = browser.find_by_tag("h1")
    assert expected in (header.text for header in headers)
    assert "Forgotten your password?" in browser.html


def test_study_link_from_home_page_list(browser, live_server, study):
    browser.visit(live_server.url)
    _study_list = browser.find_by_id("study_list")
    _study_page = _study_list.find_element_by_link_text(study.label).first_click()
    assert study.get_absolute_url() in browser.url
    assert study.name in browser.html

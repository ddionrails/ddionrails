# -*- coding: utf-8 -*-

""" Functional test cases for browser interaction with the ddionrails project """


import pytest

pytestmark = [pytest.mark.functional, pytest.mark.django_db] #pylint: disable=invalid-name


def test_get_contact_page_from_home(browser, live_server):
    browser.visit(live_server.url)
    browser.find_link_by_text("Contact / feedback").first.click()
    heading = browser.find_by_tag("h1").first
    expected = "Contact / feedback"
    assert expected == heading.text


def test_get_imprint_page_from_home(browser, live_server):
    browser.visit(live_server.url)
    browser.find_link_by_text("Imprint").first.click()
    heading = browser.find_by_tag("h1").first
    expected = "Imprint"
    assert expected == heading.text


def test_get_search_page_from_home(browser, live_server):
    browser.visit(live_server.url)
    browser.find_link_by_text("Search").first.click()
    assert "Keep my filters" in browser.html


def test_get_login_page_from_home(browser, live_server):
    browser.visit(live_server.url)
    browser.find_link_by_text("Register / log in").first.click()
    assert "User login" in browser.html


def test_get_back_home_from_other_page(browser, search_url):
    browser.visit(search_url)
    browser.find_link_by_text("paneldata.org").first.click()
    expected = "paneldata.org"
    assert expected == browser.title


def test_get_register_page_from_login(browser, login_url):
    browser.visit(login_url)
    browser.find_link_by_partial_href("register").first.click()
    assert "User registration" in browser.html


def test_get_password_reset_page_from_login(browser, login_url):
    browser.visit(login_url)
    browser.find_link_by_partial_href("password_reset").first.click()
    heading = browser.find_by_tag("h1").first
    expected = "Django administration"
    assert expected == heading.text
    assert "Forgotten your password?" in browser.html


def test_study_link_from_home_page_list(browser, live_server, study):
    browser.visit(live_server.url)
    browser.find_by_css("#main-container > div > div > b > a").first.click()
    assert study.get_absolute_url() in browser.url
    assert study.name in browser.html

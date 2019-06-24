# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Pytest fixtures for browser interaction with the ddionrails project """

from urllib.parse import urljoin

import pytest

SELENIUM_URL = "http://selenium:4444/wd/hub"


@pytest.fixture(scope="session")
def splinter_webdriver():
    """Override splinter webdriver name."""
    return "remote"


@pytest.fixture(scope="session")
def splinter_remote_url():
    """Override splinter webdriver name."""
    return SELENIUM_URL


@pytest.fixture()
def authenticated_browser(browser, client, live_server, user):
    """Return a browser instance with logged-in user session."""

    # credit to https://flowfx.de/blog/test-django-with-selenium-pytest-and-user-authentication/
    # ignore B106: hardcoded_password_funcar
    client.login(username=user.username, password="some-password")  # nosec
    cookie = client.cookies["sessionid"]
    browser.visit(live_server.url)
    browser.cookies.add({"sessionid": cookie.value})
    return browser


@pytest.fixture
def search_url(live_server):
    return urljoin(live_server.url, "search/")


@pytest.fixture
def login_url(live_server):
    return urljoin(live_server.url, "workspace/login/")

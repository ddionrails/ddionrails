# -*- coding: utf-8 -*-

""" Pytest fixtures for browser interaction with the ddionrails project """

from urllib.parse import urljoin

import pytest

from tests.factories import UserFactory

SELENIUM_URL = "http://selenium:4444/wd/hub"


@pytest.fixture(scope="session")
def splinter_webdriver():
    """Override splinter webdriver name."""
    return "remote"


@pytest.fixture(scope="session")
def splinter_remote_url():
    """Override splinter webdriver name."""
    return SELENIUM_URL


@pytest.fixture
def known_user():
    return UserFactory(username="some-user", password="some-password") #nosec # ignore B106: hardcoded_password_funcar


@pytest.fixture()
def authenticated_browser(browser, client, live_server, known_user):
    """Return a browser instance with logged-in user session."""

    # credit to https://flowfx.de/blog/test-django-with-selenium-pytest-and-user-authentication/
    client.login(username=known_user.username, password="some-password") #nosec # ignore B106: hardcoded_password_funcar
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

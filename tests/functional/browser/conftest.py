# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" Pytest fixtures for browser interaction with the ddionrails project """

from typing import Generator

import pytest
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

OPTS = Options()
OPTS.headless = False

SELENIUM_URL = "http://selenium-firefox:4444"


@pytest.fixture(name="server_url")
def server_url(live_server) -> str:
    return live_server.url.replace("localhost", "web")


@pytest.fixture(name="browser")
def selenium_browser(request) -> Generator[WebDriver, None, None]:
    """Provide a selenium remote webdriver."""
    options = Options()
    options.add_argument("browser.download.folderList=2")
    options.add_argument("browser.download.manager.showWhenStarting=False")

    _browser = WebDriver(SELENIUM_URL, options=options)

    if request.instance:
        request.instance.browser = _browser

    yield _browser
    _browser.quit()


@pytest.fixture()
def authenticated_browser(browser, client, live_server, user):
    """Return a browser instance with logged-in user session."""

    # credit to
    # https://flowfx.de/blog/test-django-with-selenium-pytest-and-user-authentication/
    # ignore B106: hardcoded_password_funcar
    client.login(username=user.username, password="some-password")  # nosec
    cookie = client.cookies["sessionid"]
    browser.visit(live_server.url)
    browser.cookies.add({"sessionid": cookie.value})
    return browser

# -*- coding: utf-8 -*-

""" Functional test cases for browser interaction with the ddionrails project """

from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User
from splinter.exceptions import ElementDoesNotExist

pytestmark = [
    pytest.mark.functional,
    pytest.mark.django_db,
]  # pylint: disable=invalid-name


def test_login_with_known_user(
    browser, login_url, user
):  # pylint: disable=unused-argument
    browser.visit(login_url)
    browser.fill("username", "some-user")
    browser.fill("password", "some-password")
    browser.find_by_value("Login").click()
    browser.find_link_by_text("My baskets").click()
    browser.find_link_by_text("My account").click()
    browser.find_link_by_text("Logout").click()


def test_login_redirects_to_same_page(browser, live_server, user):
    """ When a user logs in from any page, after logging in, the system should take
        the user back to the page he was visiting before logging in.
    """
    # The user starts at the contact page
    contact_url = urljoin(live_server.url, "contact/")
    browser.visit(contact_url)
    # Click log in button
    browser.find_link_by_text("Register / log in").click()
    browser.fill("username", "some-user")
    browser.fill("password", "some-password")
    browser.find_by_value("Login").click()
    # After logging in, the user should be redirected back to the contact page
    assert contact_url == browser.url


def test_login_with_unknown_user(browser, login_url):
    browser.visit(login_url)
    browser.fill("username", "unkown-user")
    browser.fill("password", "some-password")
    browser.find_by_value("Login").click()
    assert (
        "Please enter a correct username and password. "
        "Note that both fields may be case-sensitive." in browser.html
    )


def test_logout_with_known_user(authenticated_browser, login_url):
    authenticated_browser.visit(login_url)
    authenticated_browser.find_link_by_text("Logout").first.click()
    assert "sessionid" not in authenticated_browser.cookies.all()
    with pytest.raises(ElementDoesNotExist):
        authenticated_browser.find_link_by_text("My baskets").first.click()


def test_register_user(browser, live_server):
    assert 0 == User.objects.count()
    registration_url = urljoin(live_server.url, "workspace/register/")
    browser.visit(registration_url)
    browser.fill("username", "some-user")
    browser.fill("password1", "some-password")
    browser.fill("password2", "some-password")
    browser.find_by_value("Register").click()
    assert 1 == User.objects.count()


def test_create_basket(authenticated_browser, live_server, study):
    baskets_url = urljoin(live_server.url, "workspace/baskets/")
    authenticated_browser.visit(baskets_url)
    authenticated_browser.find_link_by_text("Create basket").click()
    basket_data = dict(name="some-basket", label="Some basket")
    authenticated_browser.fill("name", basket_data["name"])
    authenticated_browser.fill("label", basket_data["label"])
    authenticated_browser.select("study", study.id)
    authenticated_browser.find_by_value("Create basket").click()
    assert basket_data["name"] in authenticated_browser.html

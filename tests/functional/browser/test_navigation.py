# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Functional test cases for browser interaction with the ddionrails project """

from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.test.testcases import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from ddionrails.studies.models import Study

pytestmark = [
    pytest.mark.functional,
    pytest.mark.django_db,
]  # pylint: disable=invalid-name


@pytest.mark.usefixtures("browser", "user", "study")
@pytest.mark.django_db
class TestWorkspace(LiveServerTestCase):
    host = "web"
    browser: WebDriver
    study: Study
    user: User

    def test_get_contact_page_from_home(self):
        expected = "Contact / feedback"
        self.browser.get(self.live_server_url)
        self.browser.find_element(
            By.CSS_SELECTOR, "a[data-en='Contact / feedback']"
        ).click()
        headers = self.browser.find_elements(By.TAG_NAME, "h1")
        assert expected in (header.text for header in headers)

    def test_get_imprint_page_from_home(self):
        expected = "Imprint"
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.CSS_SELECTOR, "a[data-en='Imprint']").click()
        headers = self.browser.find_elements(By.TAG_NAME, "h1")
        assert expected in (header.text for header in headers)

    def test_get_login_page_from_home(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(
            By.CSS_SELECTOR, "a[data-en='Log In / Register']"
        ).click()
        assert "User login" in self.browser.page_source

    def test_get_back_home_from_other_page(self):
        self.browser.get(urljoin(self.live_server_url, "search"))
        self.browser.find_element(By.CSS_SELECTOR, "a[href='/']").click()
        expected = "Home | paneldata.org"
        assert expected == self.browser.title

    def test_get_register_page_from_login(self):
        self.browser.get(urljoin(self.live_server_url, "workspace/login/"))
        self.browser.find_element(
            By.CSS_SELECTOR,
            (
                "#main-container > div.row > "
                "div > div > div.card-body > p:nth-child(3) > a"
            ),
        ).click()
        assert "User registration" in self.browser.page_source

    def test_get_password_reset_page_from_login(self):
        expected = "Django administration"
        self.browser.get(urljoin(self.live_server_url, "workspace/login/"))
        self.browser.find_element(
            By.CSS_SELECTOR,
            "#main-container > div.row > div > div > div.card-body > p:nth-child(4) > a",
        ).click()
        headers = self.browser.find_elements(By.TAG_NAME, "h1")
        assert expected in (header.text for header in headers)
        assert "Forgotten your password?" in self.browser.page_source

    def test_study_link_from_home_page_list(self):
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.CSS_SELECTOR, "#study_list:nth-child(1)>b>a").click()
        assert self.study.get_absolute_url() in self.browser.current_url
        assert self.study.name in self.browser.page_source

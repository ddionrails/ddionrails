# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Functional test cases for browser interaction with the ddionrails project"""

from contextlib import ExitStack
from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.test.testcases import LiveServerTestCase
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ddionrails.studies.models import Study
from tests.model_factories import StudyFactory, UserFactory
from tests.object_factories import selenium_browser

pytestmark = [
    pytest.mark.functional,
]  # pylint: disable=invalid-name


class TestWorkspace(LiveServerTestCase):
    host = "web"
    browser: WebDriver
    study: Study
    user: User
    password: str

    def setUp(self) -> None:
        self.exit_stack = ExitStack()
        self.browser = self.exit_stack.enter_context(selenium_browser())
        self.study = StudyFactory()
        self.password = "123test"
        self.user = UserFactory(password=self.password)
        return super().setUp()

    def tearDown(self) -> None:
        self.exit_stack.close()
        return super().tearDown()

    def _login(
        self,
        user: str = "",
        go_to_login=True,
    ) -> WebDriver:
        if go_to_login:
            self.browser.get(urljoin(self.live_server_url, "workspace/login/"))

        username = self.user.username
        if user:
            username = user
        username_input = self.browser.find_element(By.ID, "id_username")
        username_input.send_keys(username)
        password_input = self.browser.find_element(By.ID, "id_password")

        password_input.send_keys(self.password)
        self.browser.find_element(
            By.CSS_SELECTOR,
            ("input[value='Login']"),
        ).click()
        return self.browser

    def test_login_with_known_user(self):
        self.browser.get(urljoin(self.live_server_url, "workspace/login/"))
        self.browser = self._login()

        actions = ActionChains(self.browser)

        element = self.browser.find_element(By.CSS_SELECTOR, "a[data-en='My Baskets']")
        actions.move_to_element(element).click().perform()

        element = self.browser.find_element(By.CSS_SELECTOR, "a[data-en='My Account']")
        actions.move_to_element(element).click().perform()

        element = self.browser.find_element(By.CSS_SELECTOR, "button[data-en='Log Out']")
        actions.move_to_element(element).click().perform()

    def test_login_redirects_to_same_page(self):  # pylint: disable=unused-argument
        """When a user logs in from any page, after logging in, the system should take
        the user back to the page he was visiting before logging in.
        """
        # The user starts at the contact page

        actions = ActionChains(self.browser)

        contact_url = urljoin(self.live_server_url, "contact/")
        self.browser.get(contact_url)
        element = self.browser.find_element(
            By.CSS_SELECTOR, "a[data-en='Log In / Register']"
        )
        actions.move_to_element(element).click().perform()
        self.browser.execute_script("arguments[0].click();", element)
        WebDriverWait(self.browser, 3).until(
            expected_conditions.presence_of_element_located((By.ID, "id_username"))
        )

        self.browser = self._login(go_to_login=False)
        # After logging in, the user should be redirected back to the contact page
        assert contact_url == self.browser.current_url

    def test_logout_with_known_user(self):
        authenticated_browser = self._login()
        authenticated_browser.get(self.live_server_url)
        authenticated_browser.implicitly_wait(2)
        authenticated_browser.find_element(
            By.CSS_SELECTOR, "button[data-en='Log Out']"
        ).click()

        WebDriverWait(authenticated_browser, 3).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "a[data-en='Log In / Register']")
            )
        )

        assert "sessionid" not in str(authenticated_browser.get_cookies())
        with pytest.raises(NoSuchElementException):
            authenticated_browser.find_element(
                By.CSS_SELECTOR, "a[data-en='My baskets']"
            ).click()

    def test_register_user(self):
        assert 1 == User.objects.count()
        registration_url = urljoin(self.live_server_url, "workspace/register/")

        self.browser.get(registration_url)

        username_input = self.browser.find_element(By.ID, "id_username")
        username_input.send_keys("some-other-user")
        password1_input = self.browser.find_element(By.ID, "id_password1")
        password1_input.send_keys("some-password")
        password2_input = self.browser.find_element(By.ID, "id_password2")
        password2_input.send_keys("some-password")
        self.browser.find_element(By.CSS_SELECTOR, "input[type=submit]").click()

        assert 2 == User.objects.count()

    def test_create_basket(self):
        baskets_url = urljoin(self.live_server_url, "workspace/baskets/")
        authenticated_browser = self._login()
        authenticated_browser.get(baskets_url)
        authenticated_browser.find_element(By.LINK_TEXT, "Create basket").click()
        basket_data = {"name": "some-basket", "label": "Some basket"}
        authenticated_browser.find_element(By.ID, "id_name").send_keys(
            basket_data["name"]
        )
        authenticated_browser.find_element(By.ID, "id_label").send_keys(
            basket_data["label"]
        )
        dropdown = Select(authenticated_browser.find_element(By.ID, "id_study"))
        dropdown.select_by_visible_text(self.study.name)
        authenticated_browser.find_element(By.CSS_SELECTOR, "input[type=submit]").click()
        assert basket_data["name"] in authenticated_browser.page_source

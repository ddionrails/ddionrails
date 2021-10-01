""" Functional test cases for JavaScript frontend."""

import unittest

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3 import PoolManager
from urllib3.util.retry import Retry

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


class TestMenu(unittest.TestCase):
    """ Test functionality of the menu bar.  """

    def setUp(self) -> None:

        options = webdriver.FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        self.browser = webdriver.Remote(
            command_executor="http://selenium-firefox:4444",
            desired_capabilities=DesiredCapabilities.FIREFOX,
            options=options,
        )
        retry_policy = Retry(total=1, backoff_factor=1, status_forcelist=[502, 503, 504])
        pool_manager = PoolManager(retries=retry_policy)
        pool_manager.request("GET", "http://nginx")
        self.browser.get("http://nginx")

    def test_study_dropdown(self) -> None:
        """ Does the study dropdown work?  """
        try:
            studies_dropdown_menu = self.browser.find_element_by_id("navbarbarDropdown")
        except NoSuchElementException as error:
            raise NoSuchElementException(msg=self.browser.page_source) from error

        aria_expanded = studies_dropdown_menu.get_attribute("aria-expanded")

        self.assertEqual("false", aria_expanded)
        studies_dropdown_menu.click()

        aria_expanded = studies_dropdown_menu.get_attribute("aria-expanded")
        self.assertEqual("true", aria_expanded)

        # self.browser.find_by_xpath(
        #    '//*[@id="navbarSupportedContent"]/ul[1]/li[2]/div/a[1]'
        # ).first.click()

    def tearDown(self) -> None:
        self.browser.quit()
        return super().tearDown()

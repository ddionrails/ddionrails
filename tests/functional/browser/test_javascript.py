""" Functional test cases for JavaScript frontend."""

import unittest

import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


class TestMenu(unittest.TestCase):
    """ Test functionality of the menu bar.  """

    def setUp(self) -> None:

        self.browser = webdriver.Remote(
            command_executor="http://selenium-firefox:4444",
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )
        self.browser.get("http://nginx")

    def test_study_dropdown(self) -> None:
        """ Does the study dropdown work?  """
        studies_dropdown_menu = self.browser.find_element_by_id("navbarbarDropdown")
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

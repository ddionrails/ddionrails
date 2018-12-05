#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

class Visitor(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_home_page(self):
        self.browser.get("http://localhost:8000")
        self.assertIn("DDI on Rails", self.browser.title)

if __name__ == "__main__":
    unittest.main(warnings='ignore')




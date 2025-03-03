# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from typing import Any
from unittest.mock import patch
from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.utils import override_settings
from django.utils.http import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver


from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from ddionrails.concepts.models import Concept
from ddionrails.studies.models import Study

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


@override_settings(DEBUG=True)
@pytest.mark.usefixtures(
    "browser",
    "user",
    "study",
    "search_test_case",
    "concept",
    "question",
    "topic",
    "variable",
)
@pytest.mark.django_db
class TestWorkspace(StaticLiveServerTestCase):

    host = "web"
    browser: WebDriver
    study: Study
    user: User
    concept: Any
    question: Any
    topic: Any
    variable: Any

    @override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
    def test_base_search(self):  # pylint: disable=unused-argument
        base_search_url = urljoin(self.live_server_url, "search/all")
        self.browser.get(base_search_url)

        WebDriverWait(self.browser, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='Search']")
            )
        )
        WebDriverWait(self.browser, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "div.sui-paging-info")
            )
        )

        paging_infor = self.browser.find_element(
            By.CSS_SELECTOR, "div.sui-paging-info"
        ).text
        self.assertTrue(paging_infor.strip().startswith("Showing"))

    @property
    def concepts_search_url(self):
        return urljoin(self.live_server_url, "search/concepts")

    @override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
    def test_concepts_search_is_accessible(self):
        self.browser.get(self.concepts_search_url)
        result_header = WebDriverWait(self.browser, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "div.sui-result__header")
            )
        )
        self.assertIn("some-concept", result_header.text)
        self.assertIn("Some Concept", result_header.text)

    #TODO: Refactor so that all search tests use the new method
    #TODO: Refactor so that separate search index is used
    @override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
    def test_concepts_search_by_label_de(self):
        self.concept.name = "pzuf01"
        self.concept.label = "satisfaction with health"
        self.concept.label_de = "zufriedenheit gesundheit"
        self.concept.save()

        query = urlencode({"Search": f'"{self.concept.label_de}"'})
        url = f"{self.concepts_search_url}?{query}"
        self.browser.get(url)
        self.assertIn("Concepts", self.browser.page_source)
        WebDriverWait(self.browser, 1).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "sui-result__header")
            )
        )
        self.assertIn(self.concept.label, self.browser.page_source)

    @property
    def publications_search_url(self):
        return urljoin(self.live_server_url, "search/publications")

    def test_publications_search_is_accessible(self):
        self.browser.get(self.publications_search_url)
        self.assertIn("Publications", self.browser.page_source)

        title = "Some publication with Umlauts"

        self.browser.find_element(By.ID, "Search-input").send_keys(title)
        self.assertIn(title, self.browser.page_source)

    def test_publications_search_study_facet_url_parameters(self):
        """Test that /search/publications?Studies=["Some Study"] is accessible
        and displays the publication
        """
        query = urlencode({"Studies": '["Some Study"]'})
        url = f"{self.publications_search_url}?{query}"
        self.browser.get(url)

        title = "Some publication with Umlauts"
        self.assertIn(title, self.browser.page_source)

    def test_publications_search_type_facet_url_parameters(self):
        """Test that http://localhost/search/publications?Types=["book"] is accessible
        and displays the publication
        """
        query = urlencode({"Types": '["book"]'})
        url = f"{self.publications_search_url}?{query}"
        self.browser.get(url)
        title = "Some publication with Umlauts"
        self.assertIn(title, self.browser.page_source)

    def test_publications_search_year_facet_url_parameters(self):
        """Test that http://localhost/search/publications?Years=["2019"] is accessible
        and displays the publication
        """
        query = urlencode({"Years": '["2019"]'})
        url = f"{self.publications_search_url}?{query}"
        self.browser.get(url)
        title = "Some publication with Umlauts"
        self.assertIn(title, self.browser.page_source)

    @property
    def questions_search_url(self):
        return urljoin(self.live_server_url, "search/questions")

    def test_questions_search_is_accessible(self):
        self.browser.get(self.questions_search_url)
        self.assertIn("Questions", self.browser.page_source)
        self.assertIn(self.question.label, self.browser.page_source)

    @property
    def topics_search_url(self):
        return urljoin(self.live_server_url, "search/topics")

    def test_topic_search_is_accessible(self):
        self.browser.get(self.topics_search_url)
        self.assertIn("Topics", self.browser.page_source)
        self.assertIn(self.topic.label, self.browser.page_source)

    @property
    def variables_search_url(self):
        return urljoin(self.live_server_url, "search/variables")

    def test_variables_search_is_accessible(self):
        self.browser.get(self.variables_search_url)
        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(self.variable.label, self.browser.page_source)

    def test_variables_search_by_label_de(self):
        variable = self.variable
        variable.name = "ple0081"
        variable.label = "Currently Smoke"
        variable.label_de = "Rauchen gegenwaertig"
        variable.save()

        # search with "ae"
        query = urlencode({"Search": f'"{variable.label_de}"'})
        url = f"{self.variables_search_url}?{query}"
        self.browser.get(url)
        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(variable.label, self.browser.page_source)

        # search with "ä"
        query = urlencode({"Search": "Rauchen gegenwärtig"})
        url = f"{self.variables_search_url}?{query}"
        self.browser.get(url)

        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(variable.label, self.browser.page_source)

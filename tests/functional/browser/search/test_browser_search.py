# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from typing import Any
from unittest import TestCase
from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.utils.http import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from ddionrails.studies.models import Study

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


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
class TestWorkspace(TestCase):

    host = "nginx"
    port = 80
    browser: WebDriver
    study: Study
    user: User
    concept: Any
    question: Any
    topic: Any
    variable: Any
    live_server_url = "http://nginx/"

    def test_base_search(self):  # pylint: disable=unused-argument
        base_search_url = urljoin(self.live_server_url, "search/")
        self.browser.get(base_search_url)
        heading = self.browser.find_element(By.CSS_SELECTOR, "#app > section > h1").text
        expected = "Search"
        self.assertEqual(expected, heading)
        expected = "Search | paneldata.org"
        self.assertEqual(expected, self.browser.title)

    @property
    def concepts_search_url(self):
        return urljoin(self.live_server_url, "search/concepts")

    def test_concepts_search_is_accessible(self):
        self.browser.get(self.concepts_search_url)

        self.assertIn("Concepts", self.browser.page_source)
        self.assertIn(self.concept.label, self.browser.page_source)

    def test_concepts_search_by_label_de(self):
        self.concept.name = "pzuf01"
        self.concept.label = "satisfaction with health"
        self.concept.label_de = "zufriedenheit gesundheit"
        self.concept.save()

        query = urlencode({"Search": f'"{self.concept.label_de}"'})
        url = f"{self.concepts_search_url}?{query}"
        self.browser.get(url)
        self.assertIn("Concepts", self.browser.page_source)
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

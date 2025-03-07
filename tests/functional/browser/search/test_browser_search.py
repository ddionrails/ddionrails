# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

from typing import Any
from urllib.parse import urljoin

import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.utils import override_settings
from django.utils.http import urlencode
from requests import get
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from ddionrails.concepts.models import Concept
from ddionrails.publications.models import Publication
from ddionrails.studies.models import Study
from tests import status
from tests.functional.search_index_fixtures import set_up_index, tear_down_index

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.search,
    pytest.mark.django_db,
]


@override_settings(DEBUG=True)
@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
@pytest.mark.usefixtures(
    "browser",
    "user",
    "study",
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

    def setUp(self) -> None:
        self.publication = Publication.objects.create(
            name="some-publication",
            title="Some Publication",
            study=self.study,
            type="book",
            year=2019,
        )
        set_up_index(self, self.concept, "concepts")
        set_up_index(self, self.publication, "publications")
        set_up_index(self, self.question, "questions")
        set_up_index(self, self.topic, "topics")
        set_up_index(self, self.variable, "variables")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "concepts")
        tear_down_index(self, "publications")
        tear_down_index(self, "questions")
        tear_down_index(self, "topics")
        tear_down_index(self, "variables")
        return super().tearDown()

    def test_search_url(self):
        response = get(urljoin(self.live_server_url, "search/"), allow_redirects=False)

        self.assertEqual(status.HTTP_302_FOUND, response.status_code)

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

    def test_concepts_search_is_accessible(self):
        self.browser.get(self.concepts_search_url)

        self.browser = _wait_for_results_to_load(self.browser, self.concepts_search_url)
        result_header = WebDriverWait(self.browser, 2).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, "div.sui-result__header")
            )
        )

        self.assertIn("some-concept", result_header.text)
        self.assertIn("Some Concept", result_header.text)

    #TODO: look into possible collisions
    def test_concepts_search_by_label_de(self):
        concept = Concept.objects.create()
        concept.name = "pzuf01_test"
        concept.label = "satisfaction with health test"
        concept.label_de = "zufriedenheit gesundheit test"
        concept.save()
        set_up_index(self, concept, "concepts")

        query = urlencode({"q": f'"{concept.label_de}"'})
        url = f"{self.concepts_search_url}?{query}"
        self.browser = _wait_for_results_to_load(self.browser, url)

        concept_label = self.browser.find_element(
            By.CLASS_NAME, "sui-result__header"
        ).text
        self.assertIn(concept.label, concept_label)

    @property
    def publications_search_url(self):
        return urljoin(self.live_server_url, "search/publications")

    def test_publications_search_is_accessible(self):
        self.browser.get(self.publications_search_url)
        self.assertIn("Publications", self.browser.page_source)

        title = self.publication.title

        self.browser = _wait_for_results_to_load(
            self.browser, self.publications_search_url
        )

        self.assertIn(title, self.browser.page_source)

    def test_publications_search_study_facet_url_parameters(self):
        """Test that /search/publications?Studies=["Some Study"] is accessible
        and displays the publication
        """
        query = urlencode(
            {
                "filters[0][field]": "study_name",
                "filters[0][values][0]": "Some Study",
                "filters[0][type]": "all",
            }
        )
        url = f"{self.publications_search_url}?{query}"
        self.browser.get(url)
        self.browser = _wait_for_results_to_load(self.browser, url)

        title = self.publication.title
        self.assertIn(title, self.browser.page_source)

    def test_publications_search_type_facet_url_parameters(self):
        """Test that http://localhost/search/publications?Types=["book"] is accessible
        and displays the publication
        """
        query = urlencode(
            {
                "filters[0][field]": "type",
                "filters[0][values][0]": "book",
                "filters[0][type]": "all",
            }
        )
        url = f"{self.publications_search_url}?{query}"
        self.browser = _wait_for_results_to_load(self.browser, url)
        title = self.publication.title
        self.assertIn(title, self.browser.page_source)

    def test_publications_search_year_facet_url_parameters(self):
        """Test that http://localhost/search/publications?Years=["2019"] is accessible
        and displays the publication
        """
        query = urlencode(
            {
                "filters[0][field]": "year",
                "filters[0][values][0]": "2019",
                "filters[0][type]": "all",
            }
        )
        url = f"{self.publications_search_url}?{query}"
        self.browser = _wait_for_results_to_load(self.browser, url)
        title = self.publication.title
        self.assertIn(title, self.browser.page_source)

    @property
    def questions_search_url(self):
        return urljoin(self.live_server_url, "search/questions")

    def test_questions_search_is_accessible(self):
        self.browser = _wait_for_results_to_load(self.browser, self.questions_search_url)
        self.assertIn("Questions", self.browser.page_source)
        self.assertIn(self.question.label, self.browser.page_source)

    @property
    def topics_search_url(self):
        return urljoin(self.live_server_url, "search/topics")

    def test_topic_search_is_accessible(self):
        self.browser = _wait_for_results_to_load(self.browser, self.topics_search_url)

        self.assertIn("Topics", self.browser.page_source)
        self.assertIn(self.topic.label, self.browser.page_source)

    @property
    def variables_search_url(self):
        return urljoin(self.live_server_url, "search/variables")

    def test_variables_search_is_accessible(self):
        self.browser = _wait_for_results_to_load(self.browser, self.variables_search_url)
        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(self.variable.label, self.browser.page_source)

    def test_variables_search_by_label_de(self):
        variable = self.variable
        variable.name = "ple0081"
        variable.label = "Currently Smoke"
        variable.label_de = "Rauchen gegenwaertig"
        variable.save()

        set_up_index(self, variable, "variables")

        # search with "ae"
        query = urlencode({"q": f'"{variable.label_de}"'})
        url = f"{self.variables_search_url}?{query}"
        self.browser = _wait_for_results_to_load(self.browser, url)
        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(variable.label, self.browser.page_source)

        # search with "ä"
        query = urlencode({"Search": "Rauchen gegenwärtig"})
        url = f"{self.variables_search_url}?{query}"
        self.browser.get(url)

        self.assertIn("Variables", self.browser.page_source)
        self.assertIn(variable.label, self.browser.page_source)


def _wait_for_results_to_load(_browser: WebDriver, url: str):
    for _ in range(3):
        _browser.get(url)
        try:
            _ = WebDriverWait(_browser, 1).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "sui-result__header")
                )
            )
        except BaseException:
            continue
        break
    return _browser

import json
import time

import pytest
from django.conf import settings
from elasticsearch import Elasticsearch

from imports.manager import StudyImportManager
from publications.models import Publication

pytestmark = [pytest.mark.functional]

@pytest.fixture()
def es_client():
    mapping_file = "elastic/mapping.json"
    with open(mapping_file, "r") as f:
        mapping = json.loads(f.read())
    es = Elasticsearch()

    # workaround to delete existing index
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])
    es.indices.create(index=settings.INDEX_NAME, ignore=400, body=mapping)
    # wait for elastic search index to be created
    time.sleep(0.1)
    yield es
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


@pytest.fixture()
def publication_in_search_index(settings, es_client, study):
    # redirect study data path to test data directory
    settings.IMPORT_REPO_PATH = "tests/functional/test_data/"
    manager = StudyImportManager(study)
    manager.import_single_entity("study")
    manager.import_single_entity("publications")
    # wait for indexing to be done
    time.sleep(1)


@pytest.fixture()
def search_url(live_server):
    return live_server + "/search/"


def find_facet_label_and_count_by_css_selectors(
    browser, css_selector_facet, css_selector_label, css_selector_count
):
    facet = browser.find_by_css(css_selector_facet).first
    facet_label = facet.find_by_css(css_selector_label).first
    facet_count = facet.find_by_css(css_selector_count).first
    return facet_label, facet_count


def find_type_facet_label_and_count(browser):
    css_selector_type_facet = "#main-container > app-root > results > section:nth-child(2) > div > div > div.col-md-4 > filter > div:nth-child(1)"
    css_selector_type_facet_label = "ul > li > label"
    css_selector_type_facet_count = "ul > li > span"
    return find_facet_label_and_count_by_css_selectors(
        browser,
        css_selector_type_facet,
        css_selector_type_facet_label,
        css_selector_type_facet_count,
    )


def find_period_facet_label_and_count(browser):
    css_selector_type_facet = "#main-container > app-root > results > section:nth-child(2) > div > div > div.col-md-4 > filter > div:nth-child(4)"
    css_selector_type_facet_label = "ul > a > label"
    css_selector_type_facet_count = "ul > a > span"
    return find_facet_label_and_count_by_css_selectors(
        browser,
        css_selector_type_facet,
        css_selector_type_facet_label,
        css_selector_type_facet_count,
    )


def find_study_facet_label_and_count(browser):
    css_selector_type_facet = "#main-container > app-root > results > section:nth-child(2) > div > div > div.col-md-4 > filter > div:nth-child(2)"
    css_selector_type_facet_label = "ul > a > label"
    css_selector_type_facet_count = "ul > a > span"
    return find_facet_label_and_count_by_css_selectors(
        browser,
        css_selector_type_facet,
        css_selector_type_facet_label,
        css_selector_type_facet_count,
    )


def find_publication_by_query(browser, search_url, query):
    browser.visit(search_url)

    browser.find_by_css("#searchBar > div.input-group > input").first.fill(query)
    browser.find_by_css(
        "#searchBar > div.input-group > span > button > span"
    ).first.click()

    facet_label, facet_count = find_type_facet_label_and_count(browser)
    assert "publication" == facet_label.text
    assert "1" == facet_count.text

    facet_label, facet_count = find_period_facet_label_and_count(browser)
    assert "2018" == facet_label.text
    assert "1" == facet_count.text

    facet_label, facet_count = find_study_facet_label_and_count(browser)
    assert "some-study" == facet_label.text
    assert "1" == facet_count.text

    assert browser.is_text_present("1 results")
    assert browser.is_text_present("Some Publication")
    assert browser.is_text_present("2018")

    browser.click_link_by_partial_text("Some Publication")
    assert browser.is_text_present("Go to publication")
    assert browser.is_text_present("Go to DOI")


class TestPublicationSearch:
    def test_publication_is_indexed(self, es_client, publication_in_search_index):
        assert 1 == Publication.objects.count()
        assert 1 == es_client.count(settings.INDEX_NAME, "publication").get("count")

    def test_publication_search_by_title(
        self, publication_in_search_index, browser, search_url
    ):
        query = "Some Publication"
        find_publication_by_query(browser, search_url, query)

    def test_publication_search_by_doi(
        self, publication_in_search_index, browser, search_url
    ):
        query = "some-doi"
        find_publication_by_query(browser, search_url, query)

    def test_publication_search_by_author(
        self, publication_in_search_index, browser, search_url
    ):
        query = "Surname, Firstname"
        find_publication_by_query(browser, search_url, query)

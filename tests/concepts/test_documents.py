# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.concepts app """

from os import getenv
from typing import Any
from unittest import TestCase

import pytest
from django.forms.models import model_to_dict
from django.test import LiveServerTestCase, override_settings

from ddionrails.concepts.documents import ConceptDocument, TopicDocument
from ddionrails.concepts.models import Concept
from ddionrails.studies.models import Study
from tests.functional.search_index_fixtures import set_up_index, tear_down_index

INDEX_PREFIX = getenv("ELASTICSEARCH_DSL_INDEX_PREFIX", "")


pytestmark = [
    pytest.mark.search,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]

TEST_CASE = TestCase()




@override_settings(DEBUG=True)
@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
@pytest.mark.usefixtures("variable_with_concept", "topic", "concept")
class TestDocuments( LiveServerTestCase):
    variable_with_concept: Any
    topic: Any
    concept: Any

    def setUp(self) -> None:
        set_up_index(self, self.concept, "concepts")
        set_up_index(self, self.topic, "topics")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "concepts")
        tear_down_index(self, "topics")
        return super().tearDown()

    def test_concept_search_document_fields(self):
        variable = self.variable_with_concept

        study = variable.dataset.study
        study_label = "Some Study"
        study_label_de = "Eine Studie"
        study.label = study_label
        study.label_de = study_label_de
        study.save()

        concept = variable.concept
        concept.topics.add(self.topic)
        concept.save()
        set_up_index(self, self.variable_with_concept, "variables")
        set_up_index(self, concept, "concepts")

        search = ConceptDocument.search().query("match_all")

        expected_count = 1
        assert expected_count == search.count()

        response = search.execute()
        document = response.hits[0]

        # test meta
        assert str(concept.id) == document.meta.id
        assert document.meta.index in ("testing_concepts", "concepts")

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            instance=concept,
            fields=("name", "label", "label_de", "description", "description_de"),
        )

        # add relations to expected dictionary
        expected["study_name"] = study_label
        expected["study_name_de"] = study_label_de
        expected["study"] = {
            "name": variable.dataset.study.name,
            "label": variable.dataset.study.label,
            "label_de": variable.dataset.study.label_de,
        }
        # generate result dictionary from search document
        result = document.to_dict()
        for key, value in expected.items():
            self.assertEqual(value, result[key], msg=f"Problem in {key}")
        for key in result.keys():
            TEST_CASE.assertIn(key, expected)
        assert expected == result


    def test_search_concept_by_label_de(self):
        result = ConceptDocument.search().query("match", label_de="Konzept").count()
        expected = 1
        assert expected == result


    def test_topic_search_document_fields(self):
        search = TopicDocument.search().query("match_all")
        expected: Any = 1
        assert expected == search.count()

        response = search.execute()
        document = response.hits[0]

        # test meta
        assert str(self.topic.id) == document.meta.id
        assert document.meta.index in ("testing_topics", "topics")

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            self.topic, fields=("name", "label", "label_de", "description", "description_de")
        )
        # add relations to expected dictionary
        expected["study_name"] = self.topic.study.title()
        expected["study_name_de"] = self.topic.study.label
        expected["id"] = str(self.topic.id)
        expected["study"] = {
            "name": self.topic.study.name,
            "label": self.topic.study.label,
        }

        # generate result dictionary from search document
        result = document.to_dict()
        assert expected == result

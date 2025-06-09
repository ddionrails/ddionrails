# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for documents in ddionrails.data app"""

from os import getenv

import pytest
from django.forms.models import model_to_dict
from django.test import LiveServerTestCase

from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.documents import VariableDocument
from ddionrails.data.models.variable import Variable
from tests.functional.search_index_fixtures import set_up_index, tear_down_index

INDEX_PREFIX = getenv("ELASTICSEARCH_DSL_INDEX_PREFIX", "")

pytestmark = [pytest.mark.search]


@pytest.mark.usefixtures(
    "variable", "conceptual_dataset", "analysis_unit", "period", "dataset"
)
class TestVariableDocuments(LiveServerTestCase):
    variable: Variable
    analysis_unit: AnalysisUnit
    conceptual_dataset: ConceptualDataset
    period: Period

    def setUp(self) -> None:
        set_up_index(self, self.variable, "variables")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "variables")
        return super().tearDown()

    def test_variable_search_document_fields(self):
        search = VariableDocument.search().query("match_all")

        expected = 1
        self.assertEqual(expected, search.count())
        response = search.execute()
        document = response.hits[0]

        # test meta
        self.assertEqual(str(self.variable.id), document.meta.id)
        self.assertIn(document.meta.index, ("testing_variables", "variables"))

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            self.variable,
            fields=(
                "name",
                "label",
                "label_de",
                "description",
                "description_de",
            ),
        )
        expected["categories"] = {"labels": ["Yes"], "labels_de": ["Ja"]}
        expected["name_keyword"] = expected["name"]
        # add facets to expected dictionary
        expected["analysis_unit"] = {
            "label": "Not Categorized",
            "label_de": "Nicht Kategorisiert",
        }
        expected["conceptual_dataset"] = {
            "label": "Not Categorized",
            "label_de": "Nicht Kategorisiert",
        }
        expected["period"] = {
            "label": "Not Categorized",
            "label_de": "Nicht Kategorisiert",
        }
        expected["id"] = str(self.variable.id)
        expected["study_name"] = self.variable.dataset.study.title()
        expected["study"] = {
            "name": self.variable.dataset.study.name,
            "label": self.variable.dataset.study.name,
            "label_de": self.variable.dataset.study.name,
        }
        expected["study_name_de"] = ""

        # add relations to expected dictionary
        expected["dataset"] = {
            "name": self.variable.dataset.name,
            "label": self.variable.dataset.name,
            "label_de": self.variable.dataset.name,
        }
        # generate result dictionary from search document
        result = document.to_dict()
        for key, value in expected.items():
            self.assertEqual(value, result[key], msg=f"Problem in {key}")
        for key in result.keys():
            self.assertIn(key, expected)

    def test_variable_search_document_fields_missing_related_objects(self):
        self.variable.dataset.analysis_unit = None
        self.variable.dataset.conceptual_dataset = None
        self.variable.dataset.period = None
        self.variable.dataset.save()
        self.variable.save()

        search = VariableDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        expected = "Not Categorized"
        self.assertEqual(expected, document.analysis_unit.label)
        self.assertEqual(expected, document.conceptual_dataset.label)
        self.assertEqual(expected, document.period.label)

    def test_variable_search_document_fields_string_representing_missing(self):
        self.analysis_unit.label = "Unspecified"
        self.analysis_unit.save()
        self.conceptual_dataset.label = "none"
        self.conceptual_dataset.save()
        self.period.label = "unspecified"
        self.period.save()

        self.variable.dataset.analysis_unit = self.analysis_unit
        self.variable.dataset.conceptual_dataset = self.conceptual_dataset
        self.variable.dataset.period = self.period
        self.variable.dataset.save()
        self.variable.save()

        search = VariableDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        excepted = "Not Categorized"
        self.assertEqual(excepted, document.analysis_unit.label)
        self.assertEqual(excepted, document.conceptual_dataset.label)
        self.assertEqual(excepted, document.period.label)

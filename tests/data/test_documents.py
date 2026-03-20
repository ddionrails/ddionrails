# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for documents in ddionrails.data app"""

import re
from os import getenv

from django.forms.models import model_to_dict
from django.test import LiveServerTestCase

from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.documents import VariableDocument
from ddionrails.data.models.variable import Variable
from tests.functional.search_index_fixtures import set_up_index, tear_down_index
from tests.model_factories import (
    AnalysisUnitFactory,
    ConceptualDatasetFactory,
    DatasetFactory,
    PeriodFactory,
    StudyFactory,
    VariableFactory,
)

INDEX_PREFIX = getenv("ELASTICSEARCH_DSL_INDEX_PREFIX", "")


class TestVariableDocuments(LiveServerTestCase):
    variable: Variable
    analysis_unit: AnalysisUnit
    conceptual_dataset: ConceptualDataset
    period: Period

    @classmethod
    def setUpClass(cls) -> None:
        cls.variable = VariableFactory()
        cls.dataset = cls.variable.dataset
        cls.analysis_unit = cls.dataset.analysis_unit
        cls.conceptual_dataset = cls.dataset.conceptual_dataset
        cls.concept = cls.variable.concept
        cls.period = cls.dataset.period
        return super().setUpClass()

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
        # !!!
        # Manually select non missing categories
        # Will break if categories in test factory change
        categories_labels = self.variable.categories["labels"][1]
        categories_labels_de = self.variable.categories["labels_de"][1]
        categories_labels = [re.sub(r"\[.*\]\s", "", categories_labels)]
        categories_labels_de = [re.sub(r"\[.*\]\s", "", categories_labels_de)]
        expected["categories"] = {
            "labels": categories_labels,
            "labels_de": categories_labels_de,
        }
        expected["name_keyword"] = expected["name"]
        # add facets to expected dictionary
        expected["analysis_unit"] = {
            "label": self.analysis_unit.label,
            "label_de": self.analysis_unit.label_de,
        }
        expected["conceptual_dataset"] = {
            "label": self.conceptual_dataset.label,
            "label_de": self.conceptual_dataset.label_de,
        }
        expected["period"] = {
            "label": self.period.label,
            "label_de": self.period.label_de,
        }
        expected["id"] = str(self.variable.id)
        expected["study_name"] = self.variable.dataset.study.title()
        expected["study"] = {
            "name": self.variable.dataset.study.name,
            "label": self.variable.dataset.study.label,
            "label_de": self.variable.dataset.study.label_de,
        }
        expected["study_name_de"] = self.variable.dataset.study.label_de

        # add relations to expected dictionary
        expected["dataset"] = {
            "name": self.variable.dataset.name,
            "label": self.variable.dataset.label,
            "label_de": self.variable.dataset.label_de,
        }
        expected["concept"] = {
            "label": self.concept.label,
            "label_de": self.concept.label_de,
        }
        # generate result dictionary from search document
        result = document.to_dict()
        for key, value in expected.items():
            self.assertEqual(value, result[key], msg=f"Problem in {key}")
        for key in result.keys():
            self.assertIn(key, expected)


class variable_search_with_missing(LiveServerTestCase):

    def setUp(self) -> None:
        self.dataset = DatasetFactory(
            analysis_unit=None,
            conceptual_dataset=None,
            period=None,
        )
        self.variable = VariableFactory(dataset=self.dataset)
        set_up_index(self, self.variable, "variables")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "variables")
        return super().tearDown()

    def test_variable_search_document_fields_missing_related_objects(self):

        search = VariableDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        expected = "Not Categorized"
        self.assertEqual(expected, document.analysis_unit.label)
        self.assertEqual(expected, document.conceptual_dataset.label)
        self.assertEqual(expected, document.period.label)


class variable_search_with_unspecified(LiveServerTestCase):

    def setUp(self) -> None:
        study = StudyFactory()
        analysis_unit = AnalysisUnitFactory(study=study, label="Unspecified")
        conceptual_dataset = ConceptualDatasetFactory(study=study, label="none")
        period = PeriodFactory(study=study, label="unspecified")
        self.dataset = DatasetFactory(
            analysis_unit=analysis_unit,
            conceptual_dataset=conceptual_dataset,
            period=period,
        )
        self.variable = VariableFactory(dataset=self.dataset)
        set_up_index(self, self.variable, "variables")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "variables")
        return super().tearDown()

    def test_variable_search_document_fields_string_representing_missing(self):
        search = VariableDocument.search().query("match_all")
        response = search.execute()
        document = response.hits[0]

        excepted = "Not Categorized"
        self.assertEqual(excepted, document.analysis_unit.label)
        self.assertEqual(excepted, document.conceptual_dataset.label)
        self.assertEqual(excepted, document.period.label)

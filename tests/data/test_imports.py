# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,protected-access
"""Test cases for importer classes in ddionrails.data app"""

import csv
import os
import unittest
from io import StringIO
from pathlib import Path
from typing import Dict, TypedDict
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase

from ddionrails.concepts.imports import concept_import
from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.imports import (
    DatasetImport,
    DatasetJsonImport,
    TransformationImport,
    VariableImport,
)
from ddionrails.data.models import Dataset, Transformation, Variable
from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study
from tests.concepts.factories import ConceptFactory, TopicFactory
from tests.file_factories import TMPCSV, TMPJSON
from tests.model_factories import DatasetFactory, StudyFactory, VariableFactory

TEST_CASE = TestCase()


class TestDatasetImport(TestCase):
    """Tests for csv based dataset imports"""

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.dataset = DatasetFactory(study=self.study)
        self.dataset_csv_importer = DatasetImport("DUMMY.csv", self.study)
        return super().setUp()

    @patch(
        "ddionrails.data.imports.DatasetImport._import_dataset_links",
        new_callable=MagicMock,
    )
    def test__import_dataset_links_method_gets_called(self, mocked_import_dataset_links):
        valid_dataset_data = {"dataset_name": "some-dataset"}
        self.dataset_csv_importer.import_element(valid_dataset_data)
        mocked_import_dataset_links.assert_called_once()

    def test__import_dataset_links_method_with_minimal_fields(self):
        """This import needs already existing dataset and study in the database."""
        valid_dataset_data = {"name": self.dataset.name}
        self.assertEqual(1, Dataset.objects.count())
        self.dataset_csv_importer._import_dataset_links(  # pylint: disable=protected-access
            valid_dataset_data
        )
        self.assertEqual(1, Dataset.objects.count())
        _dataset = Dataset.objects.get(name=valid_dataset_data["name"])

        analysis_unit = AnalysisUnit.objects.get(name="none")
        conceptual_dataset = ConceptualDataset.objects.get(name="none")
        period = Period.objects.get(name="none")

        # check relations are set correctly
        self.assertEqual(_dataset.analysis_unit, analysis_unit)
        self.assertEqual(_dataset.conceptual_dataset, conceptual_dataset)
        self.assertEqual(_dataset.period, period)

    def test__import_dataset_links_method_with_more_fields(self):
        """This import needs already existing dataset and study in the database."""
        analysis_unit_name = "some-analysis-unit"
        conceptual_dataset_name = "some-conceptual-dataset-name"
        period_name = "some-period-name"

        valid_dataset_data = {
            "name": self.dataset.name,
            "label": self.dataset.label,
            "description": self.dataset.description,
            "analysis_unit": analysis_unit_name,
            "conceptual_dataset": conceptual_dataset_name,
            "period_name": period_name,
        }

        self.assertEqual(1, Dataset.objects.count())
        self.dataset_csv_importer._import_dataset_links(  # pylint: disable=protected-access
            valid_dataset_data
        )
        self.assertEqual(1, Dataset.objects.count())
        dataset = Dataset.objects.get(name=valid_dataset_data["name"])

        self.assertEqual(dataset.analysis_unit.name, "some-analysis-unit")
        self.assertEqual(dataset.conceptual_dataset.name, "some-conceptual-dataset-name")
        self.assertEqual(dataset.period.name, "some-period-name")


class TestDatasetJsonImport(TestCase):

    def test_execute_import_method(self):
        self.assertEqual(0, Variable.objects.count())
        self.assertEqual(0, Dataset.objects.count())
        content = [{"study": "soep-test", "dataset": "bp", "variable": "pid"}]
        tmp_file = TMPJSON(content)
        dataset_json_importer = DatasetJsonImport(tmp_file.name, StudyFactory())
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()

    def test_import_dataset_method_with_dictionary(self):
        self.assertEqual(0, Variable.objects.count())
        self.assertEqual(0, Dataset.objects.count())

        variable = VariableFactory()
        content = [
            {
                "study": variable.dataset.study.name,
                "dataset": variable.dataset.name,
                "variable": variable.name,
            }
        ]
        tmp_file = TMPJSON(content)
        with patch.object(
            DatasetJsonImport, "_import_variable"
        ) as mocked_import_variable:
            mocked_import_variable.return_value = variable
            dataset_json_importer = DatasetJsonImport(tmp_file.name, StudyFactory())
            with patch(**tmp_file.import_patch_arguments):
                dataset_json_importer.read_file()
                dataset_json_importer.execute_import()
                self.assertTrue(mocked_import_variable.called)

    def test_import_variable_method(self):
        self.assertEqual(0, Variable.objects.count())
        self.assertEqual(0, Dataset.objects.count())
        dataset = DatasetFactory()
        self.assertEqual(1, Dataset.objects.count())
        content = [
            {
                "study": dataset.study.name,
                "dataset": dataset.name,
                "variable": "some-variable",
                "statistics": {"names": ["valid", "invalid"], "values": ["1", "0"]},
                "scale": "cat",
                "categories": {
                    "frequencies": [1, 0],
                    "labels": [
                        "[-6] Version of questionnaire with modified filtering",
                        "[1] Yes",
                    ],
                    "labels_de": [
                        "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
                        "[1] Ja",
                    ],
                    "values": ["-6", "1"],
                    "missings": [True, False],
                },
            }
        ]
        tmp_file = TMPJSON(content, file_name=f"{dataset.name}.json")
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, dataset.study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()

        self.assertEqual(1, Dataset.objects.count())

        sort_id = 0
        self.assertEqual(1, Variable.objects.count())
        variable = Variable.objects.first()
        self.assertEqual(dataset.name, variable.dataset.name)
        self.assertEqual("cat", variable.scale)
        self.assertEqual(content[0]["variable"], variable.name)
        self.assertEqual(sort_id, variable.sort_id)
        self.assertEqual("1", variable.statistics["valid"])
        self.assertEqual("0", variable.statistics["invalid"])
        self.assertEqual(1, variable.categories["frequencies"][0])
        self.assertEqual(
            "[-6] Version of questionnaire with modified filtering",
            variable.categories["labels"][0],
        )
        self.assertEqual(
            "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
            variable.categories["labels_de"][0],
        )
        self.assertEqual("-6", variable.categories["values"][0])
        self.assertTrue(variable.categories["missings"][0])
        # Test new statistics format
        expected_min = 100

        content[0]["statistics"] = {"Min.": expected_min, "Median": 200}
        del tmp_file
        tmp_file = TMPJSON(content, file_name=f"{dataset.name}.json")
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, dataset.study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()
        variable = Variable.objects.get(id=variable.id)
        self.assertEqual(expected_min, variable.statistics["Min."])

    def test_import_of_dataset_itself(self):
        study = StudyFactory()

        variable_name = "some-variable"
        dataset_name = "some-dataset"

        content = [
            {
                "study": study.name,
                "dataset": dataset_name,
                "variable": variable_name,
                "statistics": {"names": [], "values": []},
            }
        ]
        tmp_file = TMPJSON(content)
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()

        Variable.objects.get(name=variable_name, dataset__name=dataset_name)

    def test_import_variable_method_without_statistics(self):
        study = StudyFactory()

        content = [
            {
                "study": study.name,
                "dataset": "some-dataset",
                "variable": "some-variable",
                "statistics": {"names": [], "values": []},
            }
        ]
        tmp_file = TMPJSON(content)
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()

        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert {} == variable.statistics

    def test_import_variable_method_without_categories(self):

        dataset = DatasetFactory()
        self.assertEqual(0, Variable.objects.count())
        content = [
            {
                "study": dataset.study.name,
                "dataset": dataset.name,
                "variable": "some-variable",
                "statistics": {"names": ["valid", "invalid"], "values": ["1", "0"]},
                "categories": {
                    "frequencies": [],
                    "labels": [],
                    "missings": [],
                    "values": [],
                    "labels_de": [],
                },
            }
        ]

        tmp_file = TMPJSON(content, file_name=f"{dataset.name}.json")
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, dataset.study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()

        self.assertEqual(1, Variable.objects.count())
        variable = Variable.objects.first()
        self.assertEqual({}, variable.categories)

    def test_import_variable_method_with_uni_key(self):
        dataset = DatasetFactory()
        content = [
            {
                "study": dataset.study.name,
                "dataset": dataset.name,
                "variable": "some-variable",
                "uni": {"valid": 1},
            }
        ]
        tmp_file = TMPJSON(content, file_name=f"{dataset.name}.json")
        with patch(**tmp_file.import_patch_arguments):
            dataset_json_importer = DatasetJsonImport(tmp_file.name, dataset.study)
            dataset_json_importer.read_file()
            dataset_json_importer.execute_import()


class TestTransformationImport(TestCase):

    def setUp(self) -> None:
        self.origin_variable = VariableFactory(name="origin")
        study = self.origin_variable.dataset.study

        self.target_variable = VariableFactory(
            name="target", dataset=DatasetFactory(study=study)
        )
        self.assertEqual(0, Transformation.objects.count())
        self.element = {
            "origin_study_name": study.name,
            "origin_dataset_name": self.origin_variable.dataset.name,
            "origin_variable_name": self.origin_variable.name,
            "target_study_name": study.name,
            "target_dataset_name": self.target_variable.dataset.name,
            "target_variable_name": self.target_variable.name,
        }
        return super().setUp()

    def test_import_from_file(self):

        tmp_file = TMPCSV(content=[self.element])
        with patch(**tmp_file.import_patch_arguments):
            transformation_importer = TransformationImport(
                tmp_file.name, self.origin_variable.dataset.study
            )
            transformation_importer.read_file()
            transformation_importer.execute_import()

        self.assertEqual(1, Transformation.objects.count())
        transformation = Transformation.objects.first()
        self.assertEqual(self.origin_variable, transformation.origin)
        self.assertEqual(self.target_variable, transformation.target)

    def test_import_element_method_fails(self):
        study = self.origin_variable.dataset.study
        dataset = self.origin_variable.dataset
        content = [
            {
                "origin_study_name": "",
                "origin_dataset_name": "",
                "origin_variable_name": "",
                "target_study_name": study.name,
                "target_dataset_name": dataset.name,
                "target_variable_name": self.target_variable.name,
            }
        ]
        transformation_importer = TransformationImport(
            "", self.origin_variable.dataset.study
        )

        tmp_file = TMPCSV(content=content)
        with TEST_CASE.assertRaisesRegex(Variable.DoesNotExist, "Origin.*"):
            with patch(**tmp_file.import_patch_arguments):
                transformation_importer = TransformationImport(
                    tmp_file.name, self.origin_variable.dataset.study
                )
                transformation_importer.read_file()
                transformation_importer.execute_import()
        content = [
            {
                "origin_study_name": study.name,
                "origin_dataset_name": dataset.name,
                "origin_variable_name": self.origin_variable.name,
                "target_study_name": "",
                "target_dataset_name": "",
                "target_variable_name": "",
            }
        ]
        tmp_file = TMPCSV(content=content)
        with TEST_CASE.assertRaisesRegex(Variable.DoesNotExist, "Target.*"):
            with patch(**tmp_file.import_patch_arguments):
                transformation_importer = TransformationImport(
                    tmp_file.name, self.origin_variable.dataset.study
                )
                transformation_importer.read_file()
                transformation_importer.execute_import()
        del tmp_file


@pytest.mark.django_db
@pytest.mark.usefixtures(("mock_import_path"))
class TestVariableImport:
    def test_variable_import(self):
        some_dataset = DatasetFactory(name="some-dataset")
        some_dataset.save()
        ConceptFactory(name="some-concept").save()
        ConceptFactory(name="orphaned-concept").save()
        variable_path = Path(
            "tests/functional/test_data/some-study/ddionrails/variables.csv"
        )
        variable_path = variable_path.absolute()
        VariableImport.run_import(variable_path, study=some_dataset.study)
        with open(variable_path, "r", encoding="utf8") as csv_file:
            variable_names = {row["name"] for row in csv.DictReader(csv_file)}
        result = Variable.objects.filter(name__in=list(variable_names))
        TEST_CASE.assertNotEqual(0, len(result))
        TEST_CASE.assertEqual(len(variable_names), len(result))

    def test_variable_import_with_orphaned_concept(self):
        csv_path = Study().import_path()
        concept_path = csv_path.joinpath("concepts.csv")

        some_dataset = DatasetFactory(name="some-dataset")
        some_dataset.save()
        StudyImportManager(study=some_dataset.study).fix_concepts_csv()
        TopicFactory(name="some-topic")
        ConceptFactory(name="some-concept").save()
        variable_path = csv_path.joinpath("variables.csv")
        variable_path = variable_path.absolute()
        concept_import(concept_path, some_dataset.study)
        VariableImport.run_import(variable_path, study=some_dataset.study)

        with open(variable_path, "r", encoding="utf8") as csv_file:
            variable_names = {row["name"] for row in csv.DictReader(csv_file)}
        result = Variable.objects.filter(name__in=list(variable_names))
        TEST_CASE.assertNotEqual(0, len(result))
        TEST_CASE.assertEqual(len(variable_names), len(result))

    def test_variable_import_without_concept_csv(self):
        csv_path = Study().import_path()
        concept_path = csv_path.joinpath("concepts.csv")

        os.remove(concept_path)

        some_dataset = DatasetFactory(name="some-dataset")
        some_dataset.save()
        TEST_CASE.assertIsNone(
            StudyImportManager(study=some_dataset.study).fix_concepts_csv()
        )
        TEST_CASE.assertFalse(concept_path.exists())

    def test_import_element_method(self, mocker, variable_importer, dataset):
        mocked_import_variable = mocker.patch.object(VariableImport, "_import_variable")
        element = dict(dataset_name=dataset.name, variable_name="some-variable")
        variable_importer.import_element(element)
        mocked_import_variable.assert_called_once()

    def test_import_element_method_fails(
        self, mocker, capsys, variable_importer, dataset
    ):  # pylint: disable=unused-argument
        mocked_import_variable = mocker.patch.object(VariableImport, "_import_variable")
        mocked_import_variable.side_effect = KeyError
        element = dict(dataset_name="asdas", variable_name="")
        with TEST_CASE.assertRaises(KeyError):
            variable_importer.import_element(element)
        mocked_import_variable.assert_called_once()

    def test_import_variable_method(self, variable_importer, variable):
        element = dict(dataset_name=variable.dataset.name, name=variable.name)
        variable_importer._import_variable(element)  # pylint: disable=protected-access

    def test_import_variable_method_with_concept_name(self, variable_importer, variable):
        concept = ConceptFactory(name="some-concept")
        concept.save()
        element = dict(
            dataset_name=variable.dataset.name,
            name=variable.name,
            concept_name=concept.name,
            description="some-description",
        )
        variable_importer._import_variable(element)  # pylint: disable=protected-access
        variable = Variable.objects.get(id=variable.id)
        assert variable.description == element["description"]
        assert variable.concept.name == element["concept_name"]


class ImageDummy(TypedDict, total=False):
    """Typing help for TestVariableImageImport."""

    url: str


@pytest.mark.django_db
@pytest.mark.usefixtures("variable")
class TestVariableImageImport(unittest.TestCase):
    variable: Variable
    images: Dict[str, ImageDummy]

    def setUp(self):
        print(self.variable.name)
        self.images = {"image": {}, "image_de": {}}
        self.images["image"]["url"] = "https://image.com/image.png"
        self.images["image_de"]["url"] = "https://image.de/image.png"
        csv_file_handler = StringIO()
        csv_file_content = {
            "study": self.variable.dataset.study.name,
            "dataset": self.variable.dataset.name,
            "variable": self.variable.name,
            "url": self.images["image"]["url"],
            "url_de": self.images["image_de"]["url"],
        }
        csv_writer = csv.DictWriter(csv_file_handler, csv_file_content.keys())
        csv_writer.writeheader()
        csv_writer.writerow(csv_file_content)
        self.csv_file = csv_file_handler.getvalue()

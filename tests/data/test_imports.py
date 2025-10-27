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
from tests.data.factories import DatasetFactory

from .factories import VariableFactory

TEST_CASE = unittest.TestCase()


@pytest.fixture(name="dataset_csv_importer")
def _dataset_csv_importer(study):
    return DatasetImport("DUMMY.csv", study)


@pytest.fixture(name="dataset_json_importer")
def _dataset_json_importer(study):
    return DatasetJsonImport("DUMMY.csv", study)


@pytest.fixture(name="variable_importer")
def _variable_importer(study):
    return VariableImport("DUMMY.csv", study)


@pytest.fixture(name="transformation_importer")
def _transformation_importer():
    return TransformationImport("DUMMY.csv")


class TestDatasetImport:
    """Tests for csv based dataset imports"""

    @pytest.mark.django_db
    @patch(
        "ddionrails.data.imports.DatasetImport._import_dataset_links",
        new_callable=MagicMock,
    )
    def test__import_dataset_links_method_gets_called(
        self, mocked_import_dataset_links, dataset_csv_importer
    ):
        valid_dataset_data = dict(dataset_name="some-dataset")
        dataset_csv_importer.import_element(valid_dataset_data)
        mocked_import_dataset_links.assert_called_once()

    def test__import_dataset_links_method_with_minimal_fields(
        self, dataset, dataset_csv_importer
    ):
        """This import needs already existing dataset and study in the database."""
        valid_dataset_data = dict(name="some-dataset")
        assert 1 == Dataset.objects.count()
        dataset_csv_importer._import_dataset_links(  # pylint: disable=protected-access
            valid_dataset_data
        )
        assert 1 == Dataset.objects.count()
        dataset = Dataset.objects.get(name=valid_dataset_data["name"])

        analysis_unit = AnalysisUnit.objects.get(name="none")
        conceptual_dataset = ConceptualDataset.objects.get(name="none")
        period = Period.objects.get(name="none")

        # check relations are set correctly
        assert dataset.analysis_unit == analysis_unit
        assert dataset.conceptual_dataset == conceptual_dataset
        assert dataset.period == period

    def test__import_dataset_links_method_with_more_fields(
        self, dataset, dataset_csv_importer
    ):
        """This import needs already existing dataset and study in the database."""

        valid_dataset_data = dict(
            name="some-dataset",
            label="Some dataset",
            description="This is some dataset",
            analysis_unit="some-analysis-unit",
            conceptual_dataset="some-conceptual-dataset-name",
            period_name="some-period-name",
        )

        assert Dataset.objects.count() == 1
        dataset_csv_importer._import_dataset_links(  # pylint: disable=protected-access
            valid_dataset_data
        )
        assert Dataset.objects.count() == 1
        dataset = Dataset.objects.get(name=valid_dataset_data["name"])

        assert dataset.analysis_unit.name == "some-analysis-unit"
        assert dataset.conceptual_dataset.name == "some-conceptual-dataset-name"
        assert dataset.period.name == "some-period-name"


class TestDatasetJsonImport:
    def test_execute_import_method(self, mocker, dataset_json_importer):
        mocked__import_dataset = mocker.patch.object(DatasetJsonImport, "_import_dataset")
        content = """[
                        {
                            "study": "soep-test",
                            "dataset": "bp",
                            "name": "pid"
                        }
                    ]
        """
        dataset_json_importer.content = content
        dataset_json_importer.execute_import()
        mocked__import_dataset.assert_called_once()

    def test_import_dataset_method(self, mocker, dataset_json_importer):
        mocked_import_variable = mocker.patch.object(
            DatasetJsonImport, "_import_variable"
        )
        name = "some-dataset"
        content = [dict(study="some-study", dataset="some-dataset", name="some-variable")]
        dataset_json_importer._import_dataset(  # pylint: disable=protected-access
            name, content
        )
        mocked_import_variable.assert_called_once()

    def test_import_dataset_method_with_dictionary(self, mocker, dataset_json_importer):
        mocked_import_variable = mocker.patch.object(
            DatasetJsonImport, "_import_variable"
        )
        name = "some-dataset"
        content = dict(
            some_dataset=dict(
                study="some-study", dataset="some-dataset", name="some-variable"
            )
        )
        dataset_json_importer._import_dataset(  # pylint: disable=protected-access
            name, content
        )
        mocked_import_variable.assert_called_once()

    def test_import_variable_method(self, dataset_json_importer, dataset):
        assert 0 == Variable.objects.count()
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            statistics=dict(names=["valid", "invalid"], values=["1", "0"]),
            scale="cat",
            categories=dict(
                frequencies=[1, 0],
                labels=[
                    "[-6] Version of questionnaire with modified filtering",
                    "[1] Yes",
                ],
                labels_de=[
                    "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
                    "[1] Ja",
                ],
                values=["-6", "1"],
                missings=[True, False],
            ),
        )
        sort_id = 0
        dataset_json_importer._import_variable(  # pylint: disable=protected-access
            var, dataset, sort_id
        )
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert dataset == variable.dataset
        assert "cat" == variable.scale
        assert var["variable"] == variable.name
        assert sort_id == variable.sort_id
        assert "1" == variable.statistics["valid"]
        assert "0" == variable.statistics["invalid"]
        assert 1 == variable.categories["frequencies"][0]
        assert (
            "[-6] Version of questionnaire with modified filtering"
            == variable.categories["labels"][0]
        )
        assert (
            "[-6] Fragebogenversion mit geaenderter Filterfuehrung"
            == variable.categories["labels_de"][0]
        )
        assert "-6" == variable.categories["values"][0]
        assert True is variable.categories["missings"][0]
        # Test new statistics format
        expected_min = 100
        var["statistics"] = {"Min.": expected_min, "Median": 200}
        dataset_json_importer._import_variable(var, dataset, sort_id)
        variable = Variable.objects.get(id=variable.id)
        assert expected_min == variable.statistics["Min."]

    def test_import_variable_method_without_statistics(
        self, dataset_json_importer, dataset
    ):
        assert 0 == Variable.objects.count()
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            statistics=dict(names=[], values=[]),
        )
        sort_id = 0
        dataset_json_importer._import_variable(  # pylint: disable=protected-access
            var, dataset, sort_id
        )
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert {} == variable.statistics

    def test_import_variable_method_without_categories(
        self, dataset_json_importer, dataset
    ):
        assert 0 == Variable.objects.count()
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            statistics=dict(names=["valid", "invalid"], values=["1", "0"]),
            categories=dict(
                frequencies=[], labels=[], missings=[], values=[], labels_de=[]
            ),
        )
        sort_id = 0
        dataset_json_importer._import_variable(  # pylint: disable=protected-access
            var, dataset, sort_id
        )
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert {} == variable.categories

    def test_import_variable_method_with_uni_key(self, dataset_json_importer, dataset):
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            uni=dict(valid=1),
        )
        sort_id = 0
        dataset_json_importer._import_variable(  # pylint: disable=protected-access
            var, dataset, sort_id
        )


class TestTransformationImport:
    def test_import_element_method(self, transformation_importer, study, dataset):
        origin_variable = VariableFactory(name="origin")
        target_variable = VariableFactory(name="target")
        assert Transformation.objects.count() == 0
        element = dict(
            origin_study_name=study.name,
            origin_dataset_name=dataset.name,
            origin_variable_name=origin_variable.name,
            target_study_name=study.name,
            target_dataset_name=dataset.name,
            target_variable_name=target_variable.name,
        )
        transformation_importer.import_element(element)

        assert 1 == Transformation.objects.count()
        transformation = Transformation.objects.first()
        assert transformation.origin == origin_variable
        assert transformation.target == target_variable

    @pytest.mark.django_db
    def test_import_element_method_fails(self, transformation_importer, study, dataset):
        origin_variable = VariableFactory(name="origin")
        target_variable = VariableFactory(name="target")
        element = dict(
            origin_study_name="",
            origin_dataset_name="",
            origin_variable_name="",
            target_study_name=study.name,
            target_dataset_name=dataset.name,
            target_variable_name=target_variable.name,
        )
        with TEST_CASE.assertRaisesRegex(Variable.DoesNotExist, "Origin.*"):
            transformation_importer.import_element(element)
        element = dict(
            origin_study_name=study.name,
            origin_dataset_name=dataset.name,
            origin_variable_name=origin_variable.name,
            target_study_name="",
            target_dataset_name="",
            target_variable_name="",
        )
        with TEST_CASE.assertRaisesRegex(Variable.DoesNotExist, "Target.*"):
            transformation_importer.import_element(element)


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

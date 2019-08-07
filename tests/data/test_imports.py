# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for importer classes in ddionrails.data app """

import pytest

from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.imports import DatasetJsonImport
from ddionrails.data.models import Dataset, Variable

pytestmark = [pytest.mark.data, pytest.mark.imports]


@pytest.fixture
def dataset_json_importer(study):
    return DatasetJsonImport("DUMMY.csv", study)


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
        dataset_json_importer._import_dataset(name, content)
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
        dataset_json_importer._import_dataset(name, content)
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
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(var, dataset, sort_id)
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert dataset == variable.dataset
        assert "cat" == variable.scale
        assert var["variable"] == variable.name
        assert sort_id + 1 == variable.sort_id
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
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(var, dataset, sort_id)
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert dict() == variable.statistics

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
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(var, dataset, sort_id)
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
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(
            var, dataset, sort_id
        )  # pylint: disable=protected-access

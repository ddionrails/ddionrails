# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for importer classes in ddionrails.data app """

import pytest

from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.imports import DatasetImport, DatasetJsonImport, VariableImport
from ddionrails.data.models import Dataset, Variable

pytestmark = [pytest.mark.data, pytest.mark.imports]


@pytest.fixture
def dataset_csv_importer(study):
    return DatasetImport("DUMMY.csv", study)


@pytest.fixture
def dataset_json_importer(study):
    return DatasetJsonImport("DUMMY.csv", study)


@pytest.fixture
def variable_importer(study):
    return VariableImport("DUMMY.csv", study)


class TestDatasetImport:
    """ Tests for csv based dataset imports """

    @pytest.mark.django_db
    def test__import_dataset_links_method_gets_called(self, mocker, dataset_csv_importer):
        valid_dataset_data = dict(dataset_name="some-dataset")
        mocker.patch("ddionrails.data.imports.DatasetImport._import_dataset_links")
        dataset_csv_importer.import_element(valid_dataset_data)
        DatasetImport._import_dataset_links.assert_called_once()

    def test__import_dataset_links_method_with_minimal_fields(
        self, dataset, mocker, dataset_csv_importer
    ):
        """ This import method needs an already existing dataset and study in the database """
        valid_dataset_data = dict(dataset_name="some-dataset")
        assert 1 == Dataset.objects.count()
        dataset_csv_importer._import_dataset_links(
            valid_dataset_data
        )  # pylint: disable=protected-access
        assert 1 == Dataset.objects.count()
        dataset = Dataset.objects.get(name=valid_dataset_data["dataset_name"])

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
        """ This import method needs an already existing dataset and study in the database """

        valid_dataset_data = dict(
            dataset_name="some-dataset",
            label="Some dataset",
            description="This is some dataset",
            analysis_unit_name="some-analysis-unit",
            conceptual_dataset_name="some-conceptual-dataset-name",
            period_name="some-period-name",
        )

        assert Dataset.objects.count() == 1
        dataset_csv_importer._import_dataset_links(valid_dataset_data)
        assert Dataset.objects.count() == 1
        dataset = Dataset.objects.get(name=valid_dataset_data["dataset_name"])

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


class TestVariableImport:
    def test_import_element_method(self, mocker, variable_importer, dataset):
        mocked_import_variable_links = mocker.patch.object(
            VariableImport, "_import_variable_links"
        )
        element = dict(dataset_name=dataset.name, variable_name="some-variable")
        variable_importer.import_element(element)
        mocked_import_variable_links.assert_called_once()

    def test_import_element_method_fails(
        self, mocker, capsys, variable_importer, dataset
    ):  # pylint: disable=unused-argument
        mocked_import_variable_links = mocker.patch.object(
            VariableImport, "_import_variable_links"
        )
        mocked_import_variable_links.side_effect = KeyError
        element = dict(dataset_name="asdas", variable_name="")
        variable_importer.import_element(element)
        mocked_import_variable_links.assert_called_once()

    def test_import_variable_links_method(self, variable_importer, variable):
        element = dict(dataset_name=variable.dataset.name, variable_name=variable.name)
        variable_importer._import_variable_links(
            element
        )  # pylint: disable=protected-access

    def test_import_variable_links_method_with_concept_name(
        self, variable_importer, variable
    ):
        element = dict(
            dataset_name=variable.dataset.name,
            variable_name=variable.name,
            concept_name="some-concept",
            description="some-description",
        )
        variable_importer._import_variable_links(element)
        variable = Variable.objects.get(id=variable.id)
        assert variable.description == element["description"]
        assert variable.concept.name == element["concept_name"]

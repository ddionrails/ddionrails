import logging

import pytest

from data.imports import (
    DatasetImport,
    DatasetJsonImport,
    TransformationImport,
    VariableImport,
)
from data.models import Dataset, Transformation, Variable

from .factories import VariableFactory

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


@pytest.fixture
def transformation_importer():
    return TransformationImport("DUMMY.csv")


class TestDatasetImport:
    """ Tests for csv based dataset imports """

    # def test_dataset_csv_import_with_invalid_data(
    #     self, db, dataset_csv_importer, empty_data
    # ):
    #
    #     with pytest.raises(KeyError) as excinfo:
    #         dataset_csv_importer.import_element(empty_data)

    def test__import_dataset_links_method_gets_called(
        self, db, mocker, dataset_csv_importer
    ):
        valid_dataset_data = dict(dataset_name="some-dataset")
        mocker.patch("data.imports.DatasetImport._import_dataset_links")
        dataset_csv_importer.import_element(valid_dataset_data)
        DatasetImport._import_dataset_links.assert_called_once()

    def test__import_dataset_links_method_with_minimal_fields(
        self, dataset, mocker, dataset_csv_importer
    ):
        """ This import method needs an already existing dataset and study in the database """
        valid_dataset_data = dict(dataset_name="some-dataset")
        assert Dataset.objects.count() == 1
        dataset_csv_importer._import_dataset_links(valid_dataset_data)
        assert Dataset.objects.count() == 1
        dataset = Dataset.objects.get(name=valid_dataset_data["dataset_name"])

        # TODO: Is this behaviour intended?
        assert dataset.boost == 1.0
        assert dataset.analysis_unit_id == 1
        assert dataset.analysis_unit.name == "none"

        assert dataset.conceptual_dataset_id == 1
        assert dataset.conceptual_dataset.name == "none"

        assert dataset.period_id == 1
        assert dataset.period.name == "none"

    def test__import_dataset_links_method_with_more_fields(
        self, dataset, mocker, dataset_csv_importer
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

        assert dataset.boost == 1.0
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

    def test_import_variable_method(self, mocker, dataset_json_importer, dataset):
        mocked_set_elastic = mocker.patch.object(Variable, "set_elastic")
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            categories=dict(frequencies=[], labels=[]),
        )
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(var, dataset, sort_id)
        mocked_set_elastic.assert_called_once()

    def test_import_variable_method_with_uni_key(
        self, mocker, dataset_json_importer, dataset
    ):
        mocked_set_elastic = mocker.patch.object(Variable, "set_elastic")
        var = dict(
            study="some-study",
            dataset="some-dataset",
            variable="some-variable",
            uni=dict(valid=1),
        )
        dataset = dataset
        sort_id = 0
        dataset_json_importer._import_variable(var, dataset, sort_id)
        mocked_set_elastic.assert_called_once()


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
        transformation = Transformation.objects.get(id=1)
        assert Transformation.objects.count() == 1
        assert transformation.origin == origin_variable
        assert transformation.target == target_variable

    def test_import_element_method_fails(self, db, transformation_importer, caplog):
        element = dict(
            origin_study_name="",
            origin_dataset_name="",
            origin_variable_name="",
            target_study_name="",
            target_dataset_name="",
            target_variable_name="",
        )
        transformation_importer.import_element(element)

        # TODO assert logging message
        assert Transformation.objects.count() == 0


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
    ):
        mocked_import_variable_links = mocker.patch.object(
            VariableImport, "_import_variable_links"
        )
        # TODO: Insert real exception
        mocked_import_variable_links.side_effect = KeyError
        element = dict(dataset_name="asdas", variable_name="")
        variable_importer.import_element(element)
        mocked_import_variable_links.assert_called_once()
        # TODO assert logging message
        # out, err = capsys.readouterr()
        # assert "ERROR] Failed to import variable" in out

    # TODO
    def test_import_variable_links_method(self, mocker, variable_importer, variable):
        element = dict(dataset_name=variable.dataset.name, variable_name=variable.name)
        variable_importer._import_variable_links(element)

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

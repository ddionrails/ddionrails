# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for importer classes in ddionrails.concepts app """

from pathlib import Path

import pytest

from ddionrails.concepts.imports import (
    AnalysisUnitImport,
    PeriodImport,
    TopicJsonImport,
    concept_import,
    conceptual_dataset_import,
)
from ddionrails.concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from ddionrails.studies.models import TopicList

pytestmark = [pytest.mark.concepts, pytest.mark.imports]  # pylint: disable=invalid-name


@pytest.fixture
def filename():
    return "DUMMY.csv"


@pytest.fixture
def analysis_unit_importer(db, filename, study):  # pylint: disable=unused-argument
    """An analysis unit importer"""
    return AnalysisUnitImport(filename, study)


@pytest.fixture
def conceptual_dataset_importer(db, filename, study):  # pylint: disable=unused-argument
    """A conceptual dataset importer"""
    return ConceptualDatasetImport(filename, study)


@pytest.fixture
def period_importer(db, filename, study):  # pylint: disable=unused-argument
    """A period importer"""
    return PeriodImport(filename, study)


@pytest.fixture
def topic_json_importer(db, filename, study):  # pylint: disable=unused-argument
    """A topic json importer"""
    return TopicJsonImport(filename, study)


class TestAnalysisUnitImport:
    def test_import_with_valid_data(
        self, analysis_unit_importer, valid_analysis_unit_data
    ):
        response = analysis_unit_importer.import_element(valid_analysis_unit_data)
        assert isinstance(response, AnalysisUnit)
        assert response.name == valid_analysis_unit_data["analysis_unit_name"]

    def test_import_with_invalid_data(self, analysis_unit_importer, empty_data):
        response = analysis_unit_importer.import_element(empty_data)
        expected = None
        assert expected is response


class TestConceptualDatasetImport:
    def test_import_with_valid_data(self, valid_conceptual_dataset_data, study):
        csv_path = Path(
            "tests/functional/test_data/some-study/ddionrails/conceptual_datasets.csv"
        ).absolute()

        response = conceptual_dataset_import(file_path=csv_path, study=study)
        cd = ConceptualDataset.objects.get(name="some-conceptual-dataset")
        assert cd.label == "some-conceptual-dataset"


class TestPeriodImport:
    def test_import_with_valid_data(self, period_importer, valid_period_data):
        response = period_importer.import_element(valid_period_data)
        assert isinstance(response, Period)
        assert response.name == valid_period_data["period_name"]

    def test_import_with_invalid_data(self, period_importer, empty_data):
        response = period_importer.import_element(empty_data)
        expected = None
        assert expected is response


class TestTopicJsonImport:
    def test_execute_import_method(self, topic_json_importer, mocker):
        """Test that JSON string gets converted to dictionary and "_import_topic_list" gets called"""
        mocked_import_topic_list = mocker.patch.object(
            TopicJsonImport, "_import_topic_list"
        )
        topic_json_importer.content = '[{"language": "en"}]'
        topic_json_importer.execute_import()
        assert topic_json_importer.content == [{"language": "en"}]
        mocked_import_topic_list.assert_called_once()

    def test_import_topic_list_method(self, topic_json_importer):
        """Test that _import_topic_list adds "topic_languages" to Study object and creates a TopicList object"""
        study = topic_json_importer.study
        assert [] == study.topic_languages
        assert 0 == len(study.topic_languages)
        assert 0 == TopicList.objects.count()
        topic_json_importer.content = [
            {"language": "en", "topics": []},
            {"language": "de", "topics": []},
        ]
        topic_json_importer._import_topic_list()  # pylint: disable=protected-access
        study.refresh_from_db()
        assert ["de", "en"] == study.topic_languages
        assert 1 == TopicList.objects.count()
        assert topic_json_importer.content == study.topiclist.topiclist

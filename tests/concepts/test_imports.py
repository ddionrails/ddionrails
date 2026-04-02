# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for importer classes in ddionrails.concepts app"""

from pathlib import Path

from django.test import TestCase

from ddionrails.concepts.imports import (
    AnalysisUnitImport,
    PeriodImport,
    TopicJsonImport,
    conceptual_dataset_import,
)
from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.studies.models import TopicList
from tests.file_factories import TMPCSV
from tests.model_factories import StudyFactory


class TestAnalysisUnitImport(TestCase):

    def test_import_with_valid_data(self):

        study = StudyFactory()
        valid_analysis_unit = {
            "study": study.id,
            "name": "some-analysis-unit",
            "label": "Some Analysis unit",
            "description": "This is some analysis unit",
        }
        valid_analysis_unit_data = [valid_analysis_unit]
        tmp_csv = TMPCSV(content=valid_analysis_unit_data)
        importer = AnalysisUnitImport(tmp_csv.name, study)
        importer.read_file()
        importer.execute_import()
        del tmp_csv
        analysis_unit = AnalysisUnit.objects.get(
            study=study, name=valid_analysis_unit["name"]
        )
        self.assertEqual(valid_analysis_unit["label"], analysis_unit.label)

    def test_import_with_invalid_data(self):
        study = StudyFactory()
        importer = AnalysisUnitImport("", study)
        response = importer.import_element({})
        expected = None
        assert expected is response


class TestConceptualDatasetImport(TestCase):
    def test_import_with_valid_data(self):
        study = StudyFactory()
        valid_conceptual_dataset = {
            "study": study.id,
            "name": "some-conceptual-dataset",
            "label": "Some conceptual dataset",
            "description": "This is some conceptual dataset",
        }
        valid_conceptual_dataset_data = [valid_conceptual_dataset]
        tmp_csv = TMPCSV(content=valid_conceptual_dataset_data)
        csv_path = Path(tmp_csv.name).absolute()

        conceptual_dataset_import(file_path=csv_path, study=study)
        result = ConceptualDataset.objects.get(name="some-conceptual-dataset")
        del tmp_csv
        self.assertEqual(result.label, valid_conceptual_dataset["label"])


class TestPeriodImport(TestCase):
    def test_import_with_valid_data(self):

        study = StudyFactory()
        valid_period = {
            "study": study.id,
            "name": "some-period",
            "label": "Some Period",
            "description": "This is some period",
        }
        valid_period_data = [valid_period]
        tmp_csv = TMPCSV(content=valid_period_data)
        importer = PeriodImport(tmp_csv.name, study)
        importer.read_file()
        importer.execute_import()
        period = Period.objects.get(name=valid_period["name"])
        self.assertEqual(valid_period["label"], period.label)

    def test_import_with_invalid_data(self):
        study = StudyFactory()
        importer = PeriodImport("", study)
        response = importer.import_element({})
        expected = None
        assert expected is response


class TestTopicJsonImport(TestCase):

    def setUp(self) -> None:
        self.study = StudyFactory()
        self.topic_json_importer = TopicJsonImport("", self.study)
        return super().setUp()

    def test_import_topic_list_method(self):
        assert [] == self.study.topic_languages
        assert 0 == len(self.study.topic_languages)
        assert 0 == TopicList.objects.count()
        self.topic_json_importer.content = [
            {"language": "en", "topics": []},
            {"language": "de", "topics": []},
        ]
        self.topic_json_importer._import_topic_list()  # pylint: disable=protected-access
        self.study.refresh_from_db()
        assert ["de", "en"] == self.study.topic_languages
        assert 1 == TopicList.objects.count()
        assert self.topic_json_importer.content == self.study.topiclist.topiclist

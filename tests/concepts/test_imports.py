# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

"""Test cases for importer classes in ddionrails.concepts app"""

import csv
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from ddionrails.concepts.imports import (
    AnalysisUnitImport,
    TopicJsonImport,
    conceptual_dataset_import,
    period_import,
)
from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.studies.models import TopicList
from tests.file_factories import TMPCSV, destroy_tmp_path, import_data_factory
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

    def setUp(self):
        self.tmp_path, self.patch_dict, self.files, self.file_content, self.study_name = (
            import_data_factory()
        )
        self.study = StudyFactory(name=self.study_name)

        self.import_path_patch = patch(**self.patch_dict)
        self.import_path_patch.start()
        return super().setUp()

    def test_import_with_valid_data(self):
        self.assertEqual(0, Period.objects.filter(study=self.study).count())
        with open(self.tmp_path.joinpath("periods.csv"), encoding="utf8") as periods_file:
            expected_periods = {row["name"] for row in csv.DictReader(periods_file)}
        period_import(self.tmp_path.joinpath("periods.csv"), self.study)
        periods = Period.objects.filter(study=self.study, name__in=expected_periods)
        self.assertEqual(periods.count(), len(expected_periods))

    def test_import_existing(self):
        self.assertEqual(0, Period.objects.filter(study=self.study).count())
        with open(self.tmp_path.joinpath("periods.csv"), encoding="utf8") as periods_file:
            expected_periods = list({row["name"] for row in csv.DictReader(periods_file)})
        existing_period = Period(study=self.study, name=expected_periods[0])
        existing_period.save()
        self.assertEqual(1, Period.objects.filter(study=self.study).count())

        period_import(self.tmp_path.joinpath("periods.csv"), self.study)
        periods = Period.objects.filter(study=self.study, name__in=expected_periods)
        self.assertEqual(periods.count(), len(expected_periods))

        self.assertNotIn(
            Period.objects.get(study=self.study, name=expected_periods[0]).label,
            ["", None],
        )

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        destroy_tmp_path(self.tmp_path)
        return super().tearDown()


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

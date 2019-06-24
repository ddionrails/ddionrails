# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for ddionrails.concepts.resources """

import pytest
import tablib

from ddionrails.concepts.models import (
    AnalysisUnit,
    Concept,
    ConceptualDataset,
    Period,
    Topic,
)
from ddionrails.concepts.resources import (
    AnalysisUnitResource,
    ConceptResource,
    ConceptualDatasetResource,
    PeriodResource,
    TopicResource,
)

pytestmark = [pytest.mark.django_db, pytest.mark.resources]


@pytest.fixture
def topic_tablib_dataset():
    """ A tablib.Dataset containing a topic

        The topic in the second row, is a child of the topic in the first row
    """

    headers = ("study", "name", "label", "label_de", "parent")
    study = "some-study"
    name = "some-topic"
    label = "Some topic"
    label_de = "Some topic"
    parent = ""
    row_1 = (study, name, label, label_de, parent)

    name = "other-topic"
    label = "Other topic"
    label_de = "Other topic"
    parent = "some-topic"
    row_2 = (study, name, label, label_de, parent)

    dataset = tablib.Dataset(headers=headers)
    for row in (row_1, row_2):
        dataset.append(row)

    return dataset


@pytest.fixture
def concept_tablib_dataset():
    """ A tablib.Dataset containing a concept """

    headers = ("study", "name", "label", "label_de", "topic", "topic_name")
    study = "some-study"
    name = "some-concept"
    label = "Some concept"
    label_de = "Some Konzept"
    topic = "some-topic"
    topic_name = "some-topic"

    values = (study, name, label, label_de, topic, topic_name)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def analysis_unit_tablib_dataset():
    """ A tablib.Dataset containing an analysis unit """

    headers = ("study", "name", "label", "label_de", "description", "description_de")
    study = "some-study"
    name = "some-analysis-unit"
    label = "some-analysis-unit"
    label_de = "some-analysis-unit"
    description = "some-analysis-unit"
    description_de = "some-analysis-unit"

    values = (study, name, label, label_de, description, description_de)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def conceptual_dataset_tablib_dataset():
    """ A tablib.Dataset containing a conceptual dataset """

    headers = ("study", "name", "label", "label_de", "description", "description_de")
    study = "some-study"
    name = "some-conceptual-dataset"
    label = "some-conceptual-dataset"
    label_de = "some-conceptual-dataset"
    description = "some-conceptual-dataset"
    description_de = "some-conceptual-dataset"

    values = (study, name, label, label_de, description, description_de)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def period_tablib_dataset():
    """ A tablib.Dataset containing a period """

    headers = ("study_name", "name", "label", "description", "definition")
    study_name = "some-study"
    name = "some-period"
    label = "some-period"
    description = "some-period"
    definition = "some-period"

    values = (study_name, name, label, description, definition)
    return tablib.Dataset(values, headers=headers)


class TestTopicResource:
    def test_resource_import_succeeds(
        self, study, topic_tablib_dataset
    ):  # pylint: disable=unused-argument
        assert 0 == Topic.objects.count()
        result = TopicResource().import_data(topic_tablib_dataset)
        assert False is result.has_errors()
        assert 2 == Topic.objects.count()
        parent = Topic.objects.first()
        child = Topic.objects.last()

        # test attributes
        name = topic_tablib_dataset["name"][0]
        label = topic_tablib_dataset["label"][0]
        label_de = topic_tablib_dataset["label_de"][0]
        assert name == parent.name
        assert label == parent.label
        assert label_de == parent.label_de

        name = topic_tablib_dataset["name"][1]
        label = topic_tablib_dataset["label"][1]
        label_de = topic_tablib_dataset["label_de"][1]
        assert name == child.name
        assert label == child.label
        assert label_de == child.label_de

        # # test relations
        assert parent == child.parent


class TestConceptResource:
    def test_resource_import_succeeds(self, topic, concept_tablib_dataset):
        assert 0 == Concept.objects.count()

        result = ConceptResource().import_data(concept_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Concept.objects.count()

        concept = Concept.objects.first()

        # test attributes
        name = concept_tablib_dataset["name"][0]
        label = concept_tablib_dataset["label"][0]
        label_de = concept_tablib_dataset["label_de"][0]

        assert name == concept.name
        assert label == concept.label
        assert label_de == concept.label_de

        # test relations
        assert 1 == concept.topics.count()
        assert topic == concept.topics.first()


class TestAnalysisUnitResource:
    def test_resource_import_succeeds(self, study, analysis_unit_tablib_dataset):
        assert 0 == AnalysisUnit.objects.count()

        result = AnalysisUnitResource().import_data(analysis_unit_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == AnalysisUnit.objects.count()

        analysis_unit = AnalysisUnit.objects.first()

        # test attributes
        name = analysis_unit_tablib_dataset["name"][0]
        label = analysis_unit_tablib_dataset["label"][0]
        label_de = analysis_unit_tablib_dataset["label_de"][0]
        description = analysis_unit_tablib_dataset["description"][0]
        description_de = analysis_unit_tablib_dataset["description_de"][0]

        assert name == analysis_unit.name
        assert label == analysis_unit.label
        assert label_de == analysis_unit.label_de
        assert description == analysis_unit.description
        assert description_de == analysis_unit.description_de

        assert study == analysis_unit.study

    def test_resource_import_other_headers(self, study, analysis_unit_tablib_dataset):
        # rename headers, to test reverse renaming of headers
        analysis_unit_tablib_dataset.headers[
            analysis_unit_tablib_dataset.headers.index("name")
        ] = "analysis_unit_name"

        assert 0 == AnalysisUnit.objects.count()
        result = AnalysisUnitResource().import_data(analysis_unit_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == AnalysisUnit.objects.count()
        analysis_unit = AnalysisUnit.objects.first()

        # test attributes
        name = analysis_unit_tablib_dataset["name"][0]
        assert name == analysis_unit.name


class TestConceptualDatasetResource:
    def test_resource_import_succeeds(self, study, conceptual_dataset_tablib_dataset):
        assert 0 == ConceptualDataset.objects.count()

        result = ConceptualDatasetResource().import_data(
            conceptual_dataset_tablib_dataset
        )
        assert False is result.has_errors()
        assert 1 == ConceptualDataset.objects.count()

        conceptual_dataset = ConceptualDataset.objects.first()

        # test attributes
        name = conceptual_dataset_tablib_dataset["name"][0]
        label = conceptual_dataset_tablib_dataset["label"][0]
        label_de = conceptual_dataset_tablib_dataset["label_de"][0]
        description = conceptual_dataset_tablib_dataset["description"][0]
        description_de = conceptual_dataset_tablib_dataset["description_de"][0]

        assert name == conceptual_dataset.name
        assert label == conceptual_dataset.label
        assert label_de == conceptual_dataset.label_de
        assert description == conceptual_dataset.description
        assert description_de == conceptual_dataset.description_de

        assert study == conceptual_dataset.study


class TestPeriodResource:
    def test_resource_import_succeeds(self, study, period_tablib_dataset):
        assert 0 == Period.objects.count()

        result = PeriodResource().import_data(period_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Period.objects.count()

        period = Period.objects.first()

        # test attributes
        name = period_tablib_dataset["name"][0]
        label = period_tablib_dataset["label"][0]
        description = period_tablib_dataset["description"][0]

        assert name == period.name
        assert label == period.label
        assert description == period.description

        # test relations
        assert study == period.study

    def test_resource_import_other_headers(self, study, period_tablib_dataset):
        # rename headers, to test reverse renaming of headers
        period_tablib_dataset.headers[
            period_tablib_dataset.headers.index("name")
        ] = "period_name"
        period_tablib_dataset.headers[
            period_tablib_dataset.headers.index("study_name")
        ] = "study"
        assert 0 == Period.objects.count()
        result = PeriodResource().import_data(period_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Period.objects.count()
        period = Period.objects.first()

        # test attributes
        name = period_tablib_dataset["name"][0]
        assert name == period.name

        # test relations
        assert study == period.study

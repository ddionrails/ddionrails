# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for ddionrails.publications.resources """

import pytest
import tablib
from django.db import IntegrityError

from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.data.models import Dataset, Transformation, Variable
from ddionrails.data.resources import (
    DatasetResource,
    TransformationResource,
    VariableResource,
)

from .factories import VariableFactory

pytestmark = [pytest.mark.django_db, pytest.mark.resources]


@pytest.fixture(name="dataset_tablib_dataset")
def _dataset_tablib_dataset():
    """ A tablib.Dataset containing a dataset """

    headers = (
        "study_name",
        "dataset_name",
        "period_name",
        "analysis_unit_name",
        "conceptual_dataset_name",
        "label",
        "description",
    )
    study_name = "some-study"
    dataset_name = "some-dataset"
    period_name = "some-period"
    analysis_unit_name = "some-analysis-unit"
    conceptual_dataset_name = "some-conceptual-dataset"
    label = "some-dataset"
    description = "some-dataset"

    values = (
        study_name,
        dataset_name,
        period_name,
        analysis_unit_name,
        conceptual_dataset_name,
        label,
        description,
    )
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="variable_json_tablib_dataset")
def _variable_json_tablib_dataset():
    """ A tablib.Dataset containing a variable """

    headers = (
        "study",
        "dataset",
        "name",
        "label",
        "label_de",
        "categories",
        "statistics",
    )
    study = "some-study"
    dataset = "some-dataset"
    name = "some-variable"
    label = "some-variable"
    label_de = "some-variable"
    categories = {"values": [1, 0]}
    statistics = [{"names": ["max"], "values": [1]}]

    values = (study, dataset, name, label, label_de, categories, statistics)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="variable_csv_tablib_dataset")
def _variable_csv_tablib_dataset():
    """ A tablib.Dataset containing a variable """

    headers = ("study_name", "dataset_name", "variable_name", "concept_name", "image_url")
    study_name = "some-study"
    dataset_name = "some-dataset"
    variable_name = "some-variable"
    concept_name = "some-concept"
    image_url = "https://variable-image.de"

    values = (study_name, dataset_name, variable_name, concept_name, image_url)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="transformation_tablib_dataset")
def _transformation_tablib_dataset():
    """ A tablib.Dataset containing a tranformation """

    headers = (
        "origin_study_name",
        "origin_dataset_name",
        "origin_variable_name",
        "target_study_name",
        "target_dataset_name",
        "target_variable_name",
    )
    origin_study_name = "some-study"
    origin_dataset_name = "some-dataset"
    origin_variable_name = "some-variable"
    target_study_name = "some-study"
    target_dataset_name = "some-dataset"
    target_variable_name = "some-other-variable"

    values = (
        origin_study_name,
        origin_dataset_name,
        origin_variable_name,
        target_study_name,
        target_dataset_name,
        target_variable_name,
    )
    return tablib.Dataset(values, headers=headers)


@pytest.fixture(name="origin_target_variables")
def _origin_target_variables():
    return (
        VariableFactory(name="some-variable"),
        VariableFactory(name="some-other-variable"),
    )


class TestDatasetResource:
    def test_resource_import_succeeds(
        self, study, period, analysis_unit, conceptual_dataset, dataset_tablib_dataset
    ):

        assert 0 == Dataset.objects.count()
        assert 1 == AnalysisUnit.objects.count()
        assert 1 == ConceptualDataset.objects.count()
        assert 1 == Period.objects.count()
        result = DatasetResource().import_data(dataset_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Dataset.objects.count()

        dataset = Dataset.objects.first()

        # test attributes
        name = dataset_tablib_dataset["name"][0]
        label = dataset_tablib_dataset["label"][0]

        assert name == dataset.name
        assert label == dataset.label

        # test relations
        assert study == dataset.study
        # assert period == dataset.period
        assert analysis_unit == dataset.analysis_unit
        # assert conceptual_dataset == dataset.conceptual_dataset


class TestVariableResource:
    def test_resource_import_succeeds_from_json(
        self, dataset, variable_json_tablib_dataset
    ):

        assert 0 == Variable.objects.count()
        result = VariableResource().import_data(variable_json_tablib_dataset)

        assert False is result.has_errors()
        assert 1 == Variable.objects.count()

        variable = Variable.objects.first()

        # test attributes
        name = variable_json_tablib_dataset["name"][0]
        label = variable_json_tablib_dataset["label"][0]
        label_de = variable_json_tablib_dataset["label_de"][0]
        categories = variable_json_tablib_dataset["categories"][0]
        statistics = variable_json_tablib_dataset["statistics"][0]
        sort_id = variable_json_tablib_dataset["sort_id"][0]

        assert name == variable.name
        assert label == variable.label
        assert label_de == variable.label_de
        assert categories == variable.categories
        assert statistics == variable.statistics
        assert sort_id == variable.sort_id

        # test relations
        assert dataset == variable.dataset

    def test_resource_import_succeeds_from_csv(
        self, dataset, concept, variable_csv_tablib_dataset
    ):

        assert 0 == Variable.objects.count()
        result = VariableResource().import_data(variable_csv_tablib_dataset)

        assert False is result.has_errors()
        assert 1 == Variable.objects.count()

        variable = Variable.objects.first()

        # test attributes
        image_url = variable_csv_tablib_dataset["image_url"][0]
        assert image_url == variable.image_url

        # test relations
        assert dataset == variable.dataset
        assert concept == variable.concept

    def test_resource_import_succeeds_from_csv_with_empty_concept(
        self, dataset, variable_csv_tablib_dataset  # pylint: disable=unused-argument
    ):

        # remove concept from dataset
        row = list(variable_csv_tablib_dataset.lpop())
        row[row.index("some-concept")] = ""
        variable_csv_tablib_dataset.rpush(row)
        result = VariableResource().import_data(variable_csv_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert None is variable.concept


class TestTransformationResource:
    def test_resource_import_succeeds(
        self, origin_target_variables, transformation_tablib_dataset
    ):
        origin_variable, target_variable = origin_target_variables

        assert 0 == Transformation.objects.count()
        assert 2 == Variable.objects.count()
        result = TransformationResource().import_data(transformation_tablib_dataset)

        assert not result.has_errors()
        assert 1 == Transformation.objects.count()

        transformation = Transformation.objects.first()

        # test relations
        assert origin_variable == transformation.origin
        assert target_variable == transformation.target

    @pytest.mark.django_db(transaction=True)
    def test_resource_import_fails(
        self, origin_target_variables, transformation_tablib_dataset
    ):
        # make target variable in dataset invalid
        row = list(transformation_tablib_dataset.lpop())
        row[row.index("some-other-variable")] = "some-non-existing-variable"
        transformation_tablib_dataset.rpush(row)

        with pytest.raises(IntegrityError) as error:
            TransformationResource().import_data(transformation_tablib_dataset)
        assert "target_id" in error.value

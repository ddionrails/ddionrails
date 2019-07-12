# -*- coding: utf-8 -*-

""" Pytest fixtures for test cases in ddionrails.concepts app """

import pytest

from .factories import (
    AnalysisUnitFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    PeriodFactory,
)


@pytest.fixture
def concept_without_label(db):  # pylint: disable=invalid-name,unused-argument
    """ A concept without label in the database """
    return ConceptFactory(name="some-concept", description="This is some concept")


@pytest.fixture
def period_without_label(db):  # pylint: disable=invalid-name,unused-argument
    """ A period without a label in the database """
    return PeriodFactory(name="some-period", description="This is some period")


@pytest.fixture
def conceptual_dataset_without_label(db):  # pylint: disable=invalid-name,unused-argument
    """ A conceptual_dataset without a label in the database """
    return ConceptualDatasetFactory(name="some-period", description="This is some period")


@pytest.fixture
def analysis_unit_without_label(db):  # pylint: disable=invalid-name,unused-argument
    """ A analysis_unit without a label in the database """
    return AnalysisUnitFactory(name="some-period", description="This is some period")


@pytest.fixture
def period_with_range_definition(db):  # pylint: disable=invalid-name,unused-argument
    """ A period with a range period definition in the database """
    return PeriodFactory(name="some-period", description="This is some period")


@pytest.fixture
def valid_concept_data():
    """ A valid input for concept forms and imports """
    return dict(
        concept_name="some-concept",
        label="Some Concept",
        description="This is some concept",
    )


@pytest.fixture
def minimal_valid_concept_data():
    """ A minimal valid input for concept forms and imports """
    return dict(name="some-concept")


@pytest.fixture
def valid_analysis_unit_data(study):
    """ A valid input for analysis unit forms and imports, relates to study fixture """
    return dict(
        study=study.id,
        analysis_unit_name="some-analysis-unit",
        label="Some Analysis unit",
        description="This is some analysis unit",
    )


@pytest.fixture
def valid_conceptual_dataset_data():
    """ A valid input for conceptual dataset forms and imports """
    return dict(
        conceptual_dataset_name="some-conceptual-dataset",
        label="Some conceptual dataset",
        description="This is some conceptual dataset",
    )


@pytest.fixture
def valid_period_data(study):
    """ A valid input for period forms and imports, relates to study fixture """
    return dict(
        study=study.pk,
        period_name="some-period",
        label="Some Period",
        description="This is some period",
    )


@pytest.fixture
def valid_topic_data(study):
    """ A valid input for topic forms and imports """
    return dict(name="some-topic", study=study.pk)

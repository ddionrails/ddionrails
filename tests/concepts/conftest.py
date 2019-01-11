import pytest

from .factories import (
    AnalysisUnitFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    PeriodFactory,
)


@pytest.fixture
def concept_without_label(db):
    """ A concept without label in the database """
    return ConceptFactory(name="some-concept", description="This is some concept")


@pytest.fixture
def analysis_unit(db):
    """ An analysis unit in the database """
    return AnalysisUnitFactory(
        name="some-analysis-unit",
        label="Some analysis unit",
        description="This is some analysis unit",
    )


@pytest.fixture
def conceptual_dataset(db):
    """ A conceptual dataset in the database """
    return ConceptualDatasetFactory(
        name="some-conceptual-dataset",
        label="Some conceptual dataset",
        description="This is some conceptualdataset",
    )


@pytest.fixture
def period(db):
    """ A period in the database """
    return PeriodFactory(
        name="some-period",
        label="Some period",
        description="This is some period",
        definition="2018",
    )


@pytest.fixture
def period_without_label(db):
    """ A period without a label in the database """
    return PeriodFactory(name="some-period", description="This is some period")


@pytest.fixture
def period_with_range_definition(db):
    """ A period with a range period definition in the database """
    return PeriodFactory(
        name="some-period",
        description="This is some period",
        definition="2010-01:2018-12",
    )


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
def valid_analysis_unit_data():
    """ A valid input for analysis unit forms and imports """
    return dict(
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
        definition="2018",
    )

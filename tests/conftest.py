import pytest

from tests.concepts.factories import ConceptFactory
from tests.data.factories import DatasetFactory, VariableFactory
from tests.ddionrails.factories import SystemFactory
from tests.factories import UserFactory
from tests.instruments.factories import InstrumentFactory
from tests.studies.factories import StudyFactory
from tests.workspace.factories import BasketFactory


@pytest.fixture
def system(db):
    """ A system model in the database """
    return SystemFactory()


@pytest.fixture
def study(db):
    """ A study in the database """
    return StudyFactory(name="some-study", label="Some Study")


@pytest.fixture
def user(db):
    """ A user in the database """
    return UserFactory(username="some-user", password="some-password")  # noqa


@pytest.fixture
def basket(study, user):
    """ A basket in the database, relates to study and user fixture """
    return BasketFactory(name="some-basket", study=study, user=user)


@pytest.fixture
def dataset(db):
    """ A dataset in the database """
    return DatasetFactory(
        name="some-dataset", label="Some Dataset", description="This is some dataset"
    )


@pytest.fixture
def variable(db):
    """ A variable in the database """
    return VariableFactory(
        name="some-variable", label="Some Variable", description="This is some variable"
    )


@pytest.fixture
def instrument(db):
    """ An instrument in the database """
    return InstrumentFactory(
        name="some-instrument",
        label="Some Instrument",
        description="This is some instrument",
    )


@pytest.fixture()
def empty_data():
    """ Empty dictionary is used as invalid data for form and import tests """
    return {}


@pytest.fixture
def concept(db):
    """ A concept in the database """
    return ConceptFactory(
        name="some-concept", label="Some Concept", description="This is some concept"
    )

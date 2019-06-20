# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,invalid-name

""" Pytest fixtures """

from io import BytesIO

import PIL.Image
import pytest

from tests.base.factories import SystemFactory
from tests.concepts.factories import (
    AnalysisUnitFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    PeriodFactory,
    TopicFactory,
)
from tests.data.factories import DatasetFactory, TransformationFactory, VariableFactory
from tests.factories import UserFactory
from tests.instruments.factories import InstrumentFactory, QuestionFactory
from tests.publications.factories import PublicationFactory
from tests.studies.factories import StudyFactory, TopicListFactory
from tests.workspace.factories import BasketFactory


@pytest.fixture
def analysis_unit(db):
    """ An analysis unit in the database """
    return AnalysisUnitFactory(
        name="some-analysis-unit",
        label="Some analysis unit",
        description="This is some analysis unit",
    )


@pytest.fixture
def basket(study, user):
    """ A basket in the database, relates to study and user fixture """
    return BasketFactory(name="some-basket", study=study, user=user)


@pytest.fixture
def concept(db):
    """ A concept in the database """
    return ConceptFactory(
        name="some-concept", label="Some Concept", description="This is some concept"
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
def dataset(db):
    """ A dataset in the database """
    return DatasetFactory(
        name="some-dataset", label="Some Dataset", description="This is some dataset"
    )


@pytest.fixture()
def empty_data():
    """ Empty dictionary is used as invalid data for form and import tests """
    return {}


@pytest.fixture()
def image_file(request) -> BytesIO:
    """ Provides an in memory image file. """
    _file = BytesIO()
    _image = PIL.Image.new("RGBA", size=(700, 100))
    _image.save(_file, "png")
    _file.name = "test.png"
    _file.seek(0)
    if request.instance:
        request.instance.image_file = _file
    yield _file
    _file = None


@pytest.fixture
def instrument(db):
    """ An instrument in the database """
    return InstrumentFactory(
        name="some-instrument",
        label="Some Instrument",
        description="This is some instrument",
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
def publication(study):
    """ A publication in the database, relates to study fixture """
    return PublicationFactory(name="some-publication", study=study)


@pytest.fixture
def question(db, request):
    """ A question in the database """
    question = QuestionFactory(
        name="some-question",
        label="Some Question",
        description="This is some question",
        sort_id=1,
    )
    # To work with unittest
    if request.instance:
        request.instance.question = question
    return question


@pytest.fixture
def study(db):
    """ A study in the database """
    return StudyFactory(name="some-study", label="Some Study")


@pytest.fixture
def system(db):
    """ A system model in the database """
    return SystemFactory()


@pytest.fixture
def topic(db):
    """ A topic in the database """
    return TopicFactory(name="some-topic")


@pytest.fixture
def topiclist(db):
    """ A topiclist in the database """
    body = [
        {"language": "en", "topics": [{"title": "some-topic"}]},
        {"language": "de", "topics": [{"title": "some-german-topic"}]},
    ]
    return TopicListFactory(topiclist=body)


@pytest.fixture
def transformation(db):
    """ A transformation in the database """
    return TransformationFactory()


@pytest.fixture
def user(db):
    """ A user in the database """
    # ignore B106: hardcoded_password_funcarg
    return UserFactory(username="some-user", password="some-password")  # nosec


@pytest.fixture
def variable(db):
    """ A variable in the database """
    return VariableFactory(
        name="some-variable",
        label="Some Variable",
        label_de="Eine Variable",
        description="This is some variable",
        statistics=dict(valid="1", invalid="0"),
        categories={
            "frequencies": [1, 0],
            "labels": [
                "[-6] Version of questionnaire with modified filtering",
                "[1] Yes",
            ],
            "labels_de": [
                "[-6] Fragebogenversion mit geaenderter Filterfuehrung",
                "[1] Ja",
            ],
            "values": ["-6", "1"],
            "missings": [True, False],
        },
    )

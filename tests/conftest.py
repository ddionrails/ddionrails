# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,invalid-name,redefined-outer-name

""" Pytest fixtures """

import time
import unittest
import uuid
from io import BytesIO
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import mkdtemp
from typing import Any, Callable, Dict, Generator, List, Protocol, Set, TypedDict, Union
from unittest.mock import mock_open, patch

import PIL.Image
import pytest
from _pytest.fixtures import FixtureRequest
from django.conf import settings
from django.core.management import call_command
from elasticsearch.exceptions import RequestError

from ddionrails.base.models import News
from ddionrails.concepts.documents import ConceptDocument, TopicDocument
from ddionrails.data.documents import VariableDocument
from ddionrails.instruments.documents import QuestionDocument
from ddionrails.publications.documents import PublicationDocument
from tests.concepts.factories import (
    AnalysisUnitFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    PeriodFactory,
    TopicFactory,
)
from tests.data.factories import DatasetFactory, TransformationFactory, VariableFactory
from tests.factories import UserFactory
from tests.instruments.factories import (
    ConceptQuestionFactory,
    InstrumentFactory,
    QuestionFactory,
    QuestionItemFactory,
    QuestionVariableFactory,
)
from tests.publications.factories import PublicationFactory
from tests.studies.factories import StudyFactory, TopicListFactory
from tests.workspace.factories import BasketFactory

TEST_CASE = unittest.TestCase()


@pytest.fixture
def analysis_unit(db, request):
    """An analysis unit in the database"""
    analysis_unit = AnalysisUnitFactory(
        name="some-analysis-unit",
        label="Some analysis unit",
        label_de="Some analysis unit",
        description="This is some analysis unit",
        description_de="This is some analysis unit",
    )

    if request.instance:
        request.instance.analysis_unit = analysis_unit

    yield analysis_unit


@pytest.fixture(name="basket")
def _basket(request: FixtureRequest, study: StudyFactory, user: UserFactory):
    """A basket in the database, relates to study and user fixture"""
    _factory = BasketFactory(name="some-basket", study=study, user=user)
    if request.instance:
        request.instance.basket = _factory
    return _factory


@pytest.fixture
def concept(db, topic, request):
    """A concept in the database"""
    concept = ConceptFactory(
        name="some-concept",
        label="Some Concept",
        label_de="Ein Konzept",
        description="This is some concept",
    )
    root_topic = TopicFactory(
        name="root-topic",
        label="root-topic",
        label_de="root-topic",
        description="root-topic",
        description_de="root-topic",
    )
    topic.parent = root_topic
    topic.save()

    concept.topics.add(topic)
    concept.save()

    if request.instance:
        request.instance.concept = concept
    yield concept


@pytest.fixture
def concept_question(db):  # pylint: disable=unused-argument,invalid-name
    """A concept_question in the database"""
    return ConceptQuestionFactory()


@pytest.fixture
def conceptual_dataset(study, request):
    """A conceptual dataset in the database, relates to study fixture"""
    conceptual_dataset = ConceptualDatasetFactory(
        name="some-conceptual-dataset",
        label="Some conceptual dataset",
        label_de="Some conceptual dataset",
        description="This is some conceptualdataset",
        description_de="This is some conceptualdataset",
        study=study,
    )
    if request.instance:
        request.instance.conceptual_dataset = conceptual_dataset

    yield conceptual_dataset 


@pytest.fixture(name="dataset")
def _dataset(request, db):
    """A dataset in the database"""
    _factory = DatasetFactory(
        name="some-dataset", label="Some Dataset", description="This is some dataset"
    )
    if request.instance:
        request.instance.dataset = _factory
    return _factory



@pytest.fixture()
def empty_data():
    """Empty dictionary is used as invalid data for form and import tests"""
    return {}


@pytest.fixture()
def image_file(request) -> Generator[BytesIO, None, None]:
    """Provides an in memory image file."""
    _file = BytesIO()
    _image = PIL.Image.new("RGBA", size=(1, 1))
    _image.save(_file, "png")
    _file.name = "test.png"
    _file.seek(0)
    if request.instance:
        request.instance.image_file = _file
    yield _file
    del _file


@pytest.fixture(name="variable_image_file")
def _variable_image_file(request) -> Generator[Callable, None, None]:
    """Provides a function to create an in memory image file of chosen type."""

    def _image_file(file_type: str, size: int = 1) -> BytesIO:
        _file = BytesIO()
        _image = PIL.Image.new("1", size=(size, size))
        _image.save(_file, file_type)
        _file.name = f"test.{file_type}"
        _file.seek(0)
        return _file

    if request.instance:
        request.instance.variable_image_file = _image_file
    yield _image_file
    del _image_file


@pytest.fixture
@pytest.mark.usefixtures("db")
def instrument(
    request: pytest.FixtureRequest,
) -> Generator[InstrumentFactory, InstrumentFactory, None]:
    """An instrument in the database"""

    if request.instance:
        request.instance.instrument = InstrumentFactory(
            name="some-instrument",
            label="Some Instrument",
            description="This is some instrument",
        )
    yield InstrumentFactory(
        name="some-instrument",
        label="Some Instrument",
        description="This is some instrument",
    )


@pytest.fixture
def period(db, request):
    """A period in the database"""
    period = PeriodFactory(
        name="some-period", label="Some period", description="This is some period"
    )
    if request.instance:
        request.instance.period = period

    yield period 


@pytest.fixture
def publication(study):
    """A publication in the database, relates to study fixture"""
    return PublicationFactory(name="some-publication", study=study)


@pytest.fixture
def question(db, request):
    """A question in the database"""
    question = QuestionFactory(
        name="some-question",
        label="Some Question",
        description="This is some question",
        sort_id=1,
    )
    _ = QuestionItemFactory(name="1", position=0, question=question)
    # To work with unittest
    if request.instance:
        request.instance.question = question
    return question


@pytest.fixture
def question_variable(db):  # pylint: disable=unused-argument,invalid-name
    """A question_variable in the database"""
    return QuestionVariableFactory()


@pytest.fixture(name="study")
def _study(request: FixtureRequest, db: pytest.fixture):
    """A study in the database"""
    _factory = StudyFactory(name="some-study", label="Some Study")
    if request.instance:
        request.instance.study = _factory
    return _factory


@pytest.fixture
@pytest.mark.usefixtures("db")
def topic(request):
    """A topic in the database"""
    topic = TopicFactory(
        name="some-topic",
        label="some-topic",
        label_de="some-topic",
        description="some-topic",
        description_de="some-topic",
    )

    if request.instance:
        request.instance.topic = topic

    yield topic


@pytest.fixture
def topiclist(db):
    """A topiclist in the database"""
    body = [
        {"language": "en", "topics": [{"title": "some-topic"}]},
        {"language": "de", "topics": [{"title": "some-german-topic"}]},
    ]
    return TopicListFactory(topiclist=body)


@pytest.fixture
def transformation(db):
    """A transformation in the database"""
    return TransformationFactory()


@pytest.fixture
def user(db):
    """A user in the database"""
    # ignore B106: hardcoded_password_funcarg
    return UserFactory(username="some-user", password="some-password")  # nosec


@pytest.fixture(name="variable")
def _variable(request: FixtureRequest, db: pytest.fixture):
    """A variable in the database"""
    _factory = VariableFactory(
        name="some-variable",
        label="Some Variable",
        label_de="Eine Variable",
        description="This is some variable",
        statistics={"valid": "1", "invalid": "0"},
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
    if request.instance:
        request.instance.variable = _factory
    return _factory


@pytest.fixture
def variable_with_concept(variable, concept):
    """A variable in the database with a related concept"""
    variable.concept = concept
    variable.save()
    return variable


@pytest.fixture
def uuid_identifier():
    """A UUID that is used for testing views and URLConfigs"""
    return uuid.UUID("12345678123456781234567812345678")

@pytest.fixture
def publication_with_umlauts(db):  # pylint: disable=unused-argument
    """Provides a Publication containing Umlauts."""
    return PublicationFactory(
        name="1",
        title="Some publication with Umlauts",
        author="Max Müller",
        abstract="Ein schönes Buch über Fußball und Ähnliches",
        year=2019,
        type="book",
    )



class NewsFixture(TypedDict):
    """Describe news fixture output."""

    news: News
    bullet_points: List[str]


@pytest.mark.django_db
@pytest.fixture(name="news")
def _news(request) -> NewsFixture:
    """Provide a News object with its content in a separate list for easier testing."""
    the_news = News()
    bullet_points = ["test content", "more test content", "even more test content"]
    content_string = "\r\n".join(["* " + point for point in bullet_points])
    the_news.content = content_string
    the_news.save()
    if request.instance:
        request.instance.news = the_news
        request.instance.news_bullets = bullet_points
    return {"news": the_news, "bullet_points": bullet_points}


@pytest.fixture(name="mock_import_path")
def _mock_import_path(request) -> Generator[None, None, None]:
    tmp_path = Path(mkdtemp())
    csv_path = Path("tests/functional/test_data/some-study/ddionrails/").absolute()
    import_path = copytree(csv_path, tmp_path.joinpath("ddionrails"))

    patch_dict = {
        "target": "ddionrails.studies.models.Study.import_path",
        "return_value": import_path,
    }

    if request.instance:
        request.instance.patch_argument_dict = patch_dict

    with patch(**patch_dict):
        yield

    rmtree(tmp_path)


class MockOpener:
    """Wrapper to use mock_open with variable paths.

    Register paths and associate content with them.
    When patching builtin.open with MockOpener, open will
    return content dependent on the path, that is passed.
    A path that is not registered will Raise a FileNotFoundError.

    Attributes:
        files: Registered paths and their content.
        call_history: The registered paths, that were called at least once.
    """

    call_history: Set[Path]
    mocker_instances: List[Any]
    files: Dict[Path, Dict[str, Any]]

    def __init__(self):
        self.call_history = set()
        self.files = {}
        super().__init__()

    def content_written_in_path(self, path: Union[Path, str], content: str):
        """Check if content was written to a specific mock_open instance."""
        if content == self.get_content_written_in_path(Path(path)):
            return True
        return False

    def get_content_written_in_path(self, path: Path):
        """Get everything that was written to a mocked file path."""
        try:
            return self._stitch_together_write_output(self.files[Path(path)]["mocker"])
        except KeyError:
            return None

    def called_with_path(self, path: Union[str, Path]) -> bool:
        """Check if given path was opened at least once."""
        try:
            _file = self.files[Path(path)]
        except KeyError as error:
            raise ValueError("Path is not registered.") from error
        return bool(_file["mocker"])

    @staticmethod
    def _stitch_together_write_output(mocker):
        written_string = ""
        for part in mocker.write.call_args_list:
            written_string += part.args[0]
        return written_string

    def content_written(self, content: str):
        """Check if content was written to any mock_open instance."""
        for path, _ in self.files.items():
            if content == self.get_content_written_in_path(Path(path)):
                return True
        return False

    def register_file(self, path: Union[Path, str], content: str):
        """Register file paths and their associated content."""
        self.files[Path(path)] = {"content": content, "mocker": None}

    def __call__(self, *args, **kwargs):
        """Initiate mock open with given path and let it handle the rest.

        Raises:
            FileNotFoundError: The passed path is not registered.
            TypeError: Like open, the `file` argument is required.
        """
        file_path = Path(kwargs.get("file") or args[0])
        if file_path:
            if file_path in self.files:
                self.call_history.add(file_path)
                _mocker_instance = mock_open(
                    read_data=self.files[file_path]["content"]
                ).__call__()
                self.files[file_path]["mocker"] = _mocker_instance
                return _mocker_instance
            raise FileNotFoundError("2", f" No such file or directory: {file_path}")
        raise TypeError("Required argument 'file' (pos 1) not found")


# pragma: no cover
class VariableImageFile(Protocol):  # pylint: disable=too-few-public-methods
    """Type for variable Image file factory."""

    def __call__(
        self, file_type: str, size: int = 1
    ) -> BytesIO: ...  # pylint: disable=pointless-statement


class PatchImportPathArguments(TypedDict):
    """Typing for the arguments used to mock the import path.

    Attributes:
        target: The function, that would normally return the import path.
        return_value: The location of the testing import path.
    """

    target: str
    return_value: str

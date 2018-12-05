import pytest

from .factories import QuestionFactory


@pytest.fixture
def question(db):
    """ A question in the database """
    return QuestionFactory(name="some-question", label="Some Question", description="This is some question")


@pytest.fixture
def invalid_instrument_data(study):
    """ An invalid input for instrument forms and imports, relates to study fixture """
    return dict(instrument_name="", study=study.pk)


@pytest.fixture
def valid_instrument_data(study):
    """ A valid input for instrument forms and imports, relates to study fixture """
    return dict(instrument_name="some-instrument", study=study.pk)


@pytest.fixture
def invalid_question_data(instrument):
    """ An invalid input for question forms and imports, relates to instrument fixture """
    return dict(question_name="", instrument=instrument.pk)


@pytest.fixture
def valid_question_data(instrument):
    """ A valid input for question forms and imports, relates to instrument fixture """
    return dict(question_name="some-question", instrument=instrument.pk)

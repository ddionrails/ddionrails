import pytest

from .factories import ScriptFactory


@pytest.fixture
def script(db):
    """ A script in the database """
    return ScriptFactory(
        name="some-script",
        label="Some Script",
        settings='{"analysis_unit": "some-analysis-unit"}',
    )

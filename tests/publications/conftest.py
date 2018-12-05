import pytest

from .factories import PublicationFactory


@pytest.fixture
def publication(study):
    """ A publication in the database, relates to study fixture """
    return PublicationFactory(name="some-publication", study=study)

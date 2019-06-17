import pytest

from .factories import AttachmentFactory


@pytest.fixture
def attachment(db): # pylint: disable=unused-argument
    """ An attachment in the database """
    return AttachmentFactory(url="https://some-url.org")

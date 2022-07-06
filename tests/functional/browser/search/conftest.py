"""Initiate all indices."""
import pytest


@pytest.fixture
def search_test_case(  # pylint: disable=too-many-arguments
    concepts_index,
    publications_index,
    questions_index,
    topics_index,
    variables_index,
    request,
):
    """Initiate all indices with unittest compatibility."""

    if request.instance:
        request.instance.indices = (
            concepts_index,
            publications_index,
            questions_index,
            topics_index,
            variables_index,
        )
    yield

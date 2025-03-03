"""Initiate all indices."""
import pytest
from django.test.utils import override_settings


# TODO: Fix these fixtures or replace them so they write into a test index
@pytest.fixture
@override_settings(ELASTICSEARCH_DSL_INDEX_PREFIX ="testing_")
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

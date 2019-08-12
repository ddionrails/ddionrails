# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.publications app """

import pytest
from django.forms.models import model_to_dict

from ddionrails.publications.documents import PublicationDocument

pytestmark = [pytest.mark.search]


def test_publication_search_document_fields(
    publications_index, publication_with_umlauts  # pylint: disable=unused-argument
):
    search = PublicationDocument.search().query("match_all")
    expected = 1
    assert expected == search.count()
    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(publication_with_umlauts.id) == document.meta.id
    assert "testing_publications" == document.meta.index

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        publication_with_umlauts, fields=PublicationDocument.Django.fields
    )
    # add facets to expected dictionary
    expected["sub_type"] = publication_with_umlauts.sub_type
    expected["year"] = publication_with_umlauts.year
    # add relations to expected dictionary
    expected["study"] = publication_with_umlauts.study.title()
    expected["type"] = "publication"
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result

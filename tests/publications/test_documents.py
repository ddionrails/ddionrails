# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.publications app """


import pytest
from django.forms.models import model_to_dict

from ddionrails.publications.documents import PublicationDocument

pytestmark = [pytest.mark.search]


@pytest.mark.usefixtures("publications_index")
def test_publication_search_document_fields(publication_with_umlauts):
    search = PublicationDocument.search().query("match_all")
    expected_count = 1
    assert expected_count == search.count()
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
    expected["type"] = publication_with_umlauts.type
    expected["year"] = publication_with_umlauts.year
    # add relations to expected dictionary
    expected["study_name"] = publication_with_umlauts.study.title()
    expected["study"] = {
        "name": publication_with_umlauts.study.name,
        "label": publication_with_umlauts.study.label,
    }
    expected["study_name_de"] = ""
    expected["description"] = publication_with_umlauts.abstract
    expected["id"] = str(publication_with_umlauts.id)
    expected["name"] = publication_with_umlauts.name
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result

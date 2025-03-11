# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.publications app """


from django.test import LiveServerTestCase
import pytest
from django.forms.models import model_to_dict

from ddionrails.publications.documents import PublicationDocument
from ddionrails.publications.models import Publication
from tests.functional.search_index_fixtures import set_up_index, tear_down_index

pytestmark = [pytest.mark.search]

@pytest.mark.usefixtures("publication_with_umlauts")
class TestPublicationDocument(LiveServerTestCase):
    publication_with_umlauts: Publication

    def setUp(self) -> None:
        set_up_index(self, self.publication_with_umlauts, "publications")
        return super().setUp()
    def tearDown(self) -> None:
        tear_down_index(self, "publications")
        return super().tearDown()

    def test_publication_search_document_fields(self):
        search = PublicationDocument.search().query("match_all")
        expected_count = 1
        assert expected_count == search.count()
        response = search.execute()
        document = response.hits[0]

        # test meta
        assert str(self.publication_with_umlauts.id) == document.meta.id
        assert document.meta.index in ("testing_publications", "publications")

        # generate expected dictionary with attributes from model instance
        expected = model_to_dict(
            self.publication_with_umlauts, fields=PublicationDocument.Django.fields
        )
        # add facets to expected dictionary
        expected["type"] = self.publication_with_umlauts.type
        expected["year"] = self.publication_with_umlauts.year
        # add relations to expected dictionary
        expected["study_name"] = self.publication_with_umlauts.study.title()
        expected["study"] = {
            "name": self.publication_with_umlauts.study.name,
            "label": self.publication_with_umlauts.study.label,
        }
        expected["study_name_de"] = ""
        expected["description"] = self.publication_with_umlauts.abstract
        expected["id"] = str(self.publication_with_umlauts.id)
        expected["name"] = self.publication_with_umlauts.name
        # generate result dictionary from search document
        result = document.to_dict()
        assert expected == result

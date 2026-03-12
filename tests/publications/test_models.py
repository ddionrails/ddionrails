# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for models in ddionrails.publications app"""

from django.test import TestCase

from tests.model_factories import PublicationFactory


class TestPublicationModel(TestCase):
    def test_get_absolute_url_method(self):
        publication = PublicationFactory()
        expected = f"/{publication.study.name}/publ/{publication.name}"
        self.assertEqual(publication.get_absolute_url(), expected)

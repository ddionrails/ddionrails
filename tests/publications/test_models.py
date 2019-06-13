# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

""" Test cases for models in ddionrails.publications app """

import pytest

pytestmark = [pytest.mark.publications, pytest.mark.models] #pylint: disable=invalid-name


class TestPublicationModel:
    def test_string_method(self, publication):
        expected = f"/{publication.study.name}/publ/{publication.name}"
        assert str(publication) == expected

    def test_get_absolute_url_method(self, publication):
        expected = f"/{publication.study.name}/publ/{publication.name}"
        assert publication.get_absolute_url() == expected

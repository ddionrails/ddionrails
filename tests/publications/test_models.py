# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for models in ddionrails.publications app """

import pytest

pytestmark = [pytest.mark.publications, pytest.mark.models]


class TestPublicationModel:
    def test_get_absolute_url_method(self, publication):
        expected = f"/{publication.study.name}/publ/{publication.name}"
        assert publication.get_absolute_url() == expected

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for URLConf in ddionrails.concepts app"""

from uuid import uuid4

from django.test import TestCase
from django.urls import resolve, reverse


class TestConceptUrls(TestCase):
    def test_concept_list_url(self):
        concept_list_url = "concepts:concept_list"
        url = reverse(concept_list_url)
        assert resolve(url).view_name == concept_list_url

    def test_concept_detail_url_with_id(self):
        concept_detail_url_by_id = "concepts:concept_detail"
        url = reverse(concept_detail_url_by_id, kwargs={"id": uuid4()})
        assert resolve(url).view_name == concept_detail_url_by_id

    def test_concept_detail_url_with_name(self):
        concept_detail_url_by_name = "concepts:concept_detail_name"
        url = reverse(concept_detail_url_by_name, kwargs={"concept_name": "some-concept"})
        assert resolve(url).view_name == concept_detail_url_by_name

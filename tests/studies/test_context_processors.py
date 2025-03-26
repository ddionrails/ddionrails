# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" Test cases for ddionrails.studies.context_processors """

import pytest
from django.test.client import RequestFactory
from django.test.testcases import LiveServerTestCase

from ddionrails.studies.context_processors import studies_processor
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.studies]  # pylint: disable=invalid-name


@pytest.mark.usefixtures("study")
class TestContextProcessors(LiveServerTestCase):
    study: Study
    request_factory: RequestFactory

    def setUp(self) -> None:
        self.request_factory = RequestFactory()
        return super().setUp()

    def test_studies_processor_with_study(self):
        some_request = self.request_factory.get("/")
        response = studies_processor(some_request)
        queryset = Study.objects.all()
        expected = {"studies": queryset}
        assert list(expected["studies"]) == list(response["studies"])

    def test_studies_processor_without_study(self):  # pylint: disable=invalid-name
        self.study.delete()
        some_request = self.request_factory.get("/")
        response = studies_processor(some_request)
        empty_queryset = Study.objects.none()
        expected = {"studies": empty_queryset}
        assert list(expected["studies"]) == list(response["studies"])

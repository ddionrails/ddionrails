# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for views in ddionrails.instruments app"""

from uuid import uuid1

import pytest
from django.test import Client, TestCase
from django.urls import reverse

from ddionrails.studies.models import Study
from tests import status
from tests.model_factories import InstrumentFactory, QuestionFactory

pytestmark = [pytest.mark.django_db]


class TestInstrumentDetailView(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.instrument = InstrumentFactory()
        return super().setUp()

    def test_detail_view_with_existing_names(self):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={
                "study": self.instrument.study,
                "instrument_name": self.instrument.name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "instruments/instrument_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["instrument"] == self.instrument
        assert response.context["study"] == self.instrument.study

    def test_detail_view_with_invalid_study_name(self):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={
                "study": Study.objects.none(),
                "instrument_name": self.instrument.name,
            },
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_instrument_name(self):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={
                "study": self.instrument.study,
                "instrument_name": "instrument-not-in-db",
            },
        )
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestRedirectView(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.instrument = InstrumentFactory()
        self.question = QuestionFactory(instrument=self.instrument)
        return super().setUp()

    def test_instrument_redirect_view_with_valid_id(self):
        valid_id = self.instrument.id
        url = reverse("instrument_redirect", kwargs={"id": valid_id})
        response = self.client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_instrument_redirect_view_with_invalid_id(self):
        url = reverse("instrument_redirect", kwargs={"id": uuid1()})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_question_redirect_view_with_valid_id(self):
        valid_id = self.question.id
        url = reverse("question_redirect", kwargs={"id": valid_id})
        response = self.client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_question_redirect_view_with_invalid_id(self):
        url = reverse("question_redirect", kwargs={"id": uuid1()})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

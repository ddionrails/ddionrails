# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.instruments app """


import pytest
from django.urls import reverse

from ddionrails.studies.models import Study
from tests import status

pytestmark = [pytest.mark.django_db]


class TestInstrumentDetailView:
    def test_detail_view_with_existing_names(self, client, instrument):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={
                "study": instrument.study,
                "instrument_name": instrument.name,
            },
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "instruments/instrument_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["instrument"] == instrument
        assert response.context["study"] == instrument.study

    def test_detail_view_with_invalid_study_name(self, client, instrument):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={"study": Study.objects.none(), "instrument_name": instrument.name},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_instrument_name(self, client, instrument):
        url = reverse(
            "instruments:instrument_detail",
            kwargs={
                "study": instrument.study,
                "instrument_name": "instrument-not-in-db",
            },
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestInstrumentRedirectView:
    def test_redirect_view_with_valid_id(self, client, instrument):
        valid_id = instrument.id
        url = reverse("instrument_redirect", kwargs={"id": valid_id})
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_redirect_view_with_invalid_id(self, client, uuid_identifier):
        url = reverse("instrument_redirect", kwargs={"id": uuid_identifier})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestQuestionRedirectView:
    def test_redirect_view_with_valid_id(self, client, question):
        valid_id = question.id
        url = reverse("question_redirect", kwargs={"id": valid_id})
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code

    def test_redirect_view_with_invalid_id(self, client, uuid_identifier):
        url = reverse("question_redirect", kwargs={"id": uuid_identifier})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

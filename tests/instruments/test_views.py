# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.instruments app """


import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]


class TestInstrumentDetailView:
    def test_detail_view_with_existing_names(self, client, instrument):
        url = reverse(
            "inst:instrument_detail",
            kwargs={
                "study_name": instrument.study.name,
                "instrument_name": instrument.name,
            },
        )

        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        template = "instruments/instrument_detail.html"
        assert template in (t.name for t in response.templates)
        assert response.context["instrument"] == instrument
        assert response.context["study"] == instrument.study
        expected_questions = list(instrument.questions.all())
        output_questions = list(response.context["questions"])
        assert expected_questions == output_questions

    def test_detail_view_with_invalid_study_name(self):
        pass

    def test_detail_view_with_invalid_instrument_name(self):
        pass


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

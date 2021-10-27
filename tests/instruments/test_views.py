# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.instruments app """


import pytest
from django.urls import reverse

from tests import status
from tests.instruments.factories import QuestionFactory

pytestmark = [pytest.mark.django_db]


@pytest.fixture(name="compare_questions")
def _compare_questions():
    return (
        QuestionFactory(name="some-question", sort_id=1),
        QuestionFactory(name="some-other-question", sort_id=2),
    )


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

    def test_detail_view_with_invalid_study_name(self, client, instrument):
        url = reverse(
            "inst:instrument_detail",
            kwargs={"study_name": "study-not-in-db", "instrument_name": instrument.name},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_detail_view_with_invalid_instrument_name(self, client, instrument):
        url = reverse(
            "inst:instrument_detail",
            kwargs={
                "study_name": instrument.study.name,
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


class TestStudyInstrumentList:
    def test_with_valid_study_name(self, client, instrument):
        url = reverse(
            "inst:study_instrument_list", kwargs={"study_name": instrument.study.name}
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_with_invalid_study_name(self, client):
        url = reverse(
            "inst:study_instrument_list", kwargs={"study_name": "study-not-in-db"}
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestQuestionComparisonPartial:
    def test_with_valid_ids(self, client, compare_questions):
        from_question, to_question = compare_questions
        url = reverse(
            "api:question_comparison_partial",
            kwargs={"from_id": from_question.id, "to_id": to_question.id},
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        content = response.content.decode("utf-8")
        assert from_question.name in content
        assert to_question.name in content

    def test_with_invalid_from_id(self, client, compare_questions, uuid_identifier):
        _, to_question = compare_questions
        url = reverse(
            "api:question_comparison_partial",
            kwargs={"from_id": uuid_identifier, "to_id": to_question.id},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

    def test_with_invalid_to_id(self, client, compare_questions, uuid_identifier):
        from_question, _ = compare_questions
        url = reverse(
            "api:question_comparison_partial",
            kwargs={"from_id": from_question.id, "to_id": uuid_identifier},
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code

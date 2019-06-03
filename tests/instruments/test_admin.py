# -*- coding: utf-8 -*-
""" Test cases for ModelAdmins in ddionrails.instruments app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]


def test_instrument_admin_list(admin_client, instrument):
    """ Test the InstrumentAdmin changelist """
    url = reverse("admin:instruments_instrument_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_instrument_admin_detail(admin_client, instrument):
    """ Test the InstrumentAdmin change_view """
    url = reverse("admin:instruments_instrument_change", args=(instrument.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_question_admin_list(admin_client, question):
    """ Test the QuestionAdmin changelist """
    url = reverse("admin:instruments_question_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_question_admin_detail(admin_client, question):
    """ Test the QuestionAdmin change_view """
    url = reverse("admin:instruments_question_change", args=(question.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_concept_question_admin_list(admin_client, concept_question):
    """ Test the ConceptQuestionAdmin changelist """
    url = reverse("admin:instruments_conceptquestion_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_concept_question_admin_detail(admin_client, concept_question):
    """ Test the ConceptQuestionAdmin change_view """
    url = reverse("admin:instruments_conceptquestion_change", args=(concept_question.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_question_variable_admin_list(admin_client, question_variable):
    """ Test the QuestionVariableAdmin changelist """
    url = reverse("admin:instruments_questionvariable_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_question_variable_admin_detail(admin_client, question_variable):
    """ Test the QuestionVariableAdmin change_view """
    url = reverse(
        "admin:instruments_questionvariable_change", args=(question_variable.id,)
    )
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

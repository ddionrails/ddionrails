# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for ddionrails.studies.context_processors """

import pytest

from ddionrails.studies.context_processors import studies_processor
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.studies]  # pylint: disable=invalid-name


def test_studies_processor_with_study(
    study, rf
):  # pylint: disable=unused-argument,invalid-name
    some_request = rf.get("/")
    response = studies_processor(some_request)
    queryset = Study.objects.all()
    expected = dict(studies=queryset)
    assert list(expected["studies"]) == list(response["studies"])


@pytest.mark.django_db
def test_studies_processor_without_study(rf):  # pylint: disable=invalid-name
    some_request = rf.get("/")
    response = studies_processor(some_request)
    empty_queryset = Study.objects.none()
    expected = dict(studies=empty_queryset)
    assert list(expected["studies"]) == list(response["studies"])

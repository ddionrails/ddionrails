# -*- coding: utf-8 -*-
""" Test cases for ModelAdmins in ddionrails.studies app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]


def test_study_admin_list(admin_client, study):
    """ Test the StudyAdmin changelist """
    url = reverse("admin:studies_study_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_study_admin_detail(admin_client, study):
    """ Test the StudyAdmin change_view """
    url = reverse("admin:studies_study_change", args=(study.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

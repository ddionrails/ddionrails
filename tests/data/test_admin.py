# -*- coding: utf-8 -*-
""" Test cases for ModelAdmins in ddionrails.data app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]


def test_dataset_admin_list(admin_client, dataset):
    """ Test the DatasetAdmin changelist """
    url = reverse("admin:data_dataset_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_dataset_admin_detail(admin_client, dataset):
    """ Test the DatasetAdmin change_view """
    url = reverse("admin:data_dataset_change", args=(dataset.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_variable_admin_list(admin_client, variable):
    """ Test the VariableAdmin changelist """
    url = reverse("admin:data_variable_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_variable_admin_detail(admin_client, variable):
    """ Test the VariableAdmin change_view """
    url = reverse("admin:data_variable_change", args=(variable.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_transformation_admin_list(admin_client, transformation):
    """ Test the TransformationAdmin changelist """
    url = reverse("admin:data_transformation_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_transformation_admin_detail(admin_client, transformation):
    """ Test the TransformationAdmin change_view """
    url = reverse("admin:data_transformation_change", args=(transformation.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

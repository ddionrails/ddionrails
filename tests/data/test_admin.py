# -*- coding: utf-8 -*-
""" Test cases for ModelAdmins in ddionrails.data app """

import pytest
from django.urls import reverse

from tests import status

# One of the admin views in django itself
# uses {% load staticfiles %} instead {% load static %}.
# It throws a "django.utils.deprecation.RemovedInDjango30Warning"
pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]


def test_dataset_admin_list(admin_client, dataset):  # pylint: disable=unused-argument
    """ Test the DatasetAdmin changelist """
    url = reverse("admin:data_dataset_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_dataset_admin_detail(admin_client, dataset):
    """ Test the DatasetAdmin change_view """
    url = reverse("admin:data_dataset_change", args=(dataset.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_variable_admin_list(admin_client, variable):  # pylint: disable=unused-argument
    """ Test the VariableAdmin changelist """
    url = reverse("admin:data_variable_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_variable_admin_detail(admin_client, variable):
    """ Test the VariableAdmin change_view """
    url = reverse("admin:data_variable_change", args=(variable.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_transformation_admin_list(
    admin_client, transformation
):  # pylint: disable=unused-argument
    """ Test the TransformationAdmin changelist """
    url = reverse("admin:data_transformation_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_transformation_admin_detail(admin_client, transformation):
    """ Test the TransformationAdmin change_view """
    url = reverse("admin:data_transformation_change", args=(transformation.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

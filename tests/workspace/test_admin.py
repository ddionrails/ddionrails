# -*- coding: utf-8 -*-

""" Test cases for ModelAdmins in ddionrails.workspace app """

import pytest
from django.urls import reverse

from tests import status

pytestmark = [pytest.mark.django_db]


def test_basket_variable_admin_list(admin_client, basket_variable):
    """ Test the BasketVariableAdmin changelist """
    url = reverse("admin:workspace_basketvariable_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_basket_variable_admin_detail(admin_client, basket_variable):
    """ Test the BasketVariableAdmin change_view """
    url = reverse("admin:workspace_basketvariable_change", args=(basket_variable.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_basket_admin_list(admin_client, basket):
    """ Test the BasketAdmin changelist """
    url = reverse("admin:workspace_basket_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_basket_admin_detail(admin_client, basket):
    """ Test the BasketAdmin change_view """
    url = reverse("admin:workspace_basket_change", args=(basket.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_script_admin_list(admin_client, script):
    """ Test the ScriptAdmin changelist """
    url = reverse("admin:workspace_script_changelist")
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code


def test_script_admin_detail(admin_client, script):
    """ Test the ScriptAdmin change_view """
    url = reverse("admin:workspace_script_change", args=(script.id,))
    response = admin_client.get(url)
    assert status.HTTP_200_OK == response.status_code

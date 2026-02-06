# -*- coding: utf-8 -*-
"""Test cases for ModelAdmins in ddionrails.data app"""


from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from tests import status
from tests.model_factories import AdminUserFactory, TransformationFactory, VariableFactory


class TestAdmin(TestCase):
    """Test admin views"""

    admin_client: Client
    variable: VariableFactory

    def setUp(self) -> None:
        admin_password = "123test"  # nosec
        admin_user = AdminUserFactory(password=admin_password)
        self.admin_client = Client()
        self.admin_client.login(username=admin_user.username, password=admin_password)
        self.variable = VariableFactory()
        self._override_settings = override_settings(
            DEBUG_TOOLBAR_CONFIG={"SHOW_TOOLBAR_CALLBACK": lambda request: False},
        )
        self._override_settings.enable()

        return super().setUp()

    def test_dataset_admin_list(self):
        """Test the DatasetAdmin changelist"""

        url = reverse("admin:data_dataset_change", args=(str(self.variable.dataset.id),))

        response = self.admin_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_variable_admin_list(self):
        """Test the VariableAdmin changelist"""
        url = reverse("admin:data_variable_changelist")
        response = self.admin_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_variable_admin_detail(self):
        """Test the VariableAdmin change_view"""
        url = reverse("admin:data_variable_change", args=(str(self.variable.id),))
        response = self.admin_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_transformation_admin_list(self):  # pylint: disable=unused-argument
        """Test the TransformationAdmin changelist"""
        _ = TransformationFactory(origin=self.variable)
        url = reverse("admin:data_transformation_changelist")
        response = self.admin_client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_transformation_admin_detail(self):
        """Test the TransformationAdmin change_view"""
        transformation = TransformationFactory(origin=self.variable)
        url = reverse("admin:data_transformation_change", args=(str(transformation.id),))
        response = self.admin_client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def tearDown(self) -> None:
        self._override_settings.disable()
        return super().tearDown()

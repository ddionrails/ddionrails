# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name,imported-auth-user

"""Test cases for views in ddionrails.workspace app"""

import csv
from uuid import uuid1

import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable, Script
from ddionrails.workspace.models.script_metadata import ScriptMetadata
from tests import status
from tests.model_factories import BasketFactory, VariableFactory

from .factories import UserFactory


class TestOwnBasketOnlyDecorator(TestCase):

    def setUp(self) -> None:
        self.basket = BasketFactory()
        self.client = Client()
        return super().setUp()

    def test_basket_belongs_to_user(self):
        url = reverse("workspace:basket_detail", kwargs={"basket_id": self.basket.id})
        self.client.force_login(user=self.basket.user)
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_basket_belongs_to_other_user(self):
        user = self.basket.user
        other_user = UserFactory(username="other-user")
        self.basket.user = other_user
        self.basket.save()
        url = reverse("workspace:basket_detail", kwargs={"basket_id": self.basket.id})
        self.client.force_login(user=user)
        response = self.client.get(url)
        assert status.HTTP_403_FORBIDDEN == response.status_code

    @pytest.mark.django_db
    def test_basket_does_not_exist(self):
        url = reverse("workspace:basket_detail", kwargs={"basket_id": 999})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestScriptDetailView(TestCase):
    def test_script_detail_view_with_script_created_before_update(self):
        """This tests a regression that was
        introduced after updating the settings for scripts
        with a 'gender' option
        """
        basket = BasketFactory()
        client = Client()
        study = Study(name="soep-core")
        study.save()
        metadata = ScriptMetadata(study=study, metadata={})
        metadata.save()

        script = Script()
        script.name = "name"
        script.label = "label"
        script.basket = basket
        # Set the settings to the default values from before the update
        script.settings = (
            '{"path_in": "data/", "path_out": "out/", '
            '"analysis_unit": "p", "private": "t", '
            '"balanced": "t", "age_group": "adult"}'
        )
        script.save()
        url = reverse(
            "workspace:script_detail",
            kwargs={"basket_id": basket.id, "script_id": script.id},
        )
        client.force_login(user=basket.user)  # nosec
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code


class TestAccountOverview(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        return super().setUp()

    def test_account_overview_anonymous_user(self):
        url = reverse("workspace:account_overview")
        response = self.client.get(url)
        assert status.HTTP_401_UNAUTHORIZED == response.status_code

    def test_account_overview_authenticated_user(self):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse("workspace:account_overview")
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code


class TestBasketList(TestCase):

    def setUp(self) -> None:
        self.basket = BasketFactory()
        self.client = Client()
        return super().setUp()

    def test_basket_list_anonymous_user(self):
        response = self.client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = []
        basket_list = response.context["basket_list"]
        assert expected == basket_list

    def test_basket_list_authenticated_user(self):
        assert 1 == Basket.objects.count()
        self.client.force_login(user=self.basket.user)
        response = self.client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = list(Basket.objects.all())
        basket_list = response.context["basket_list"]
        assert expected == list(basket_list)


class TestAddConcept(TestCase):

    variable: VariableFactory
    client_with_referer: Client

    def setUp(self) -> None:
        self.variable = VariableFactory()
        self.client_with_referer = Client(HTTP_REFERER="/")
        return super().setUp()

    def tearDown(self) -> None:
        self.client_with_referer.logout()
        return super().tearDown()

    def test_with_invalid_concept_id(self):
        assert 0 == BasketVariable.objects.count()
        basket = BasketFactory()
        self.client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_concept",
            kwargs={"basket_id": basket.id, "concept_id": uuid1()},
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_valid_ids(self):
        assert 0 == BasketVariable.objects.count()
        basket = BasketFactory(study=self.variable.dataset.study)
        self.client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_concept",
            kwargs={
                "basket_id": basket.id,
                "concept_id": self.variable.concept.id,
            },
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert self.variable == basket_variable.variable
        assert basket == basket_variable.basket

    def test_with_invalid_basket_id(self):
        assert 0 == BasketVariable.objects.count()
        user = UserFactory()
        self.client_with_referer.force_login(user)  # nosec
        url = reverse(
            "workspace:add_concept",
            kwargs={"basket_id": 999, "concept_id": self.variable.concept.id},
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestRemoveConcept(TestCase):

    def setUp(self) -> None:
        self.variable = VariableFactory()
        self.basket = BasketFactory(variables=[self.variable])
        self.client_with_referer = Client(HTTP_REFERER="/")
        return super().setUp()

    def tearDown(self) -> None:
        self.client_with_referer.logout()
        return super().tearDown()

    def test_with_valid_ids(self):
        assert 1 == BasketVariable.objects.count()
        self.client_with_referer.force_login(user=self.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": self.basket.id,
                "concept_id": self.variable.concept.id,
            },
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_basket_id(self):
        assert 1 == BasketVariable.objects.count()
        self.client_with_referer.force_login(user=self.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": 999,
                "concept_id": self.variable.concept_id,
            },
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()

    def test_with_invalid_concept_id(self):
        assert 1 == BasketVariable.objects.count()
        self.client_with_referer.force_login(user=self.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": self.basket.id,
                "concept_id": uuid1(),
            },
        )
        response = self.client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()


class TestBasketToCsv(TestCase):

    def setUp(self) -> None:
        self.variable = VariableFactory()
        self.basket = BasketFactory(variables=[self.variable])
        self.client_with_referer = Client(HTTP_REFERER="/")
        return super().setUp()

    def tearDown(self) -> None:
        self.client_with_referer.logout()
        return super().tearDown()

    def test_with_valid_id(self):
        assert 1 == BasketVariable.objects.count()
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": self.basket.id})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code
        expected_content_type = "text/csv"
        assert expected_content_type == response["content-type"]
        content = response.content.decode("utf-8")
        expected_content_disposition = 'attachment; filename="basket.csv"'
        assert expected_content_disposition == response["Content-Disposition"]

        # test exported csv
        reader = csv.DictReader(content.splitlines())
        row = next(reader)
        assert self.variable.name == row["name"]
        assert self.variable.dataset.name == row["dataset_name"]
        assert self.variable.dataset.study.name == row["study_name"]
        assert self.variable.dataset.period.name == row["period_name"]

    def test_with_invalid_id(self):
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": 999})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestBasketDetail(TestCase):

    def setUp(self) -> None:
        self.basket = BasketFactory()
        self.client_with_referer = Client(HTTP_REFERER="/")
        return super().setUp()

    def tearDown(self) -> None:
        self.client_with_referer.logout()
        return super().tearDown()

    def test_with_valid_id(self):
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_detail", kwargs={"basket_id": self.basket.id})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_with_invalid_id(self):
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_detail", kwargs={"basket_id": 999})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestBasketSearch(TestCase):

    def setUp(self) -> None:
        self.basket = BasketFactory()
        self.client_with_referer = Client(HTTP_REFERER="/")
        return super().setUp()

    def tearDown(self) -> None:
        self.client_with_referer.logout()
        return super().tearDown()

    def test_with_valid_id(self):
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": self.basket.id})
        response = self.client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_with_invalid_id(self):
        self.client.force_login(user=self.basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": 999})
        response = self.client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestUserDelete(TransactionTestCase):

    def test_with_valid_user(self):
        client = Client()
        password = "123test"
        user = UserFactory(password=password)
        self.assertEqual(1, User.objects.count())
        self.assertTrue(client.login(username=user.username, password=password))
        url = reverse("workspace:user_delete")
        response = client.get(url)
        self.assertEqual(status.HTTP_302_FOUND, response.status_code)
        self.assertEqual(0, User.objects.count())

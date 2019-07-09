# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for views in ddionrails.workspace app """

import csv

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from ddionrails.workspace.models import Basket, BasketVariable
from tests import status

from .factories import UserFactory


@pytest.fixture
def client_with_referer():
    """ A django.test.Client with a HTTP_REFERER to test redirects """
    return Client(HTTP_REFERER="https://www.google.com")


@pytest.fixture
def basket_variable_with_concept(basket_variable, concept):
    """ A variable with a related concept in a basket """
    basket_variable.variable.concept = concept
    basket_variable.variable.save()
    return basket_variable


class TestOwnBasketOnlyDecorator:
    def test_basket_belongs_to_user(self, client, basket):
        url = reverse("workspace:basket_detail", kwargs={"basket_id": basket.id})
        client.force_login(user=basket.user)
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_basket_belongs_to_other_user(self, client, basket):
        user = basket.user
        other_user = UserFactory(username="other-user")
        basket.user = other_user
        basket.save()
        url = reverse("workspace:basket_detail", kwargs={"basket_id": basket.id})
        client.force_login(user=user)
        response = client.get(url)
        assert status.HTTP_403_FORBIDDEN == response.status_code

    @pytest.mark.django_db
    def test_basket_does_not_exist(self, client):
        url = reverse("workspace:basket_detail", kwargs={"basket_id": 999})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestScriptDetailView:
    def test_script_detail_view_with_script_created_before_update(
        self, client, basket, script
    ):
        """ This tests a regression that was introduced after updating the settings for scripts
            with a 'gender' option
        """
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
        client.login(username=basket.user, password="secret-password")  # nosec
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code


class TestAccountOverview:
    def test_account_overview_anonymous_user(self, client):
        url = reverse("workspace:account_overview")
        response = client.get(url)
        assert status.HTTP_401_UNAUTHORIZED == response.status_code

    def test_account_overview_authenticated_user(
        self, client, user
    ):  # pylint: disable=unused-argument
        client.force_login(user=user)
        url = reverse("workspace:account_overview")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code


class TestBasketList:
    def test_basket_list_anonymous_user(
        self, client, basket  # pylint: disable=unused-argument
    ):
        response = client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = []
        basket_list = response.context["basket_list"]
        assert expected == basket_list

    def test_basket_list_authenticated_user(
        self, client, basket  # pylint: disable=unused-argument
    ):
        assert 1 == Basket.objects.count()
        client.force_login(user=basket.user)
        response = client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = list(Basket.objects.all())
        basket_list = response.context["basket_list"]
        assert expected == list(basket_list)


class TestAddVariable:
    def test_with_valid_ids(self, client_with_referer, basket, variable):
        assert 0 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_variable",
            kwargs={"basket_id": basket.id, "variable_id": variable.id},
        )
        response = client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()

    def test_with_invalid_basket_id(self, client, variable):
        assert 0 == BasketVariable.objects.count()
        client.login(username="some-user", password="some-password")  # nosec
        url = reverse(
            "workspace:add_variable", kwargs={"basket_id": 1, "variable_id": variable.id}
        )
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_variable_id(self, client_with_referer, basket, uuid_identifier):
        assert 0 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_variable",
            kwargs={"basket_id": basket.id, "variable_id": uuid_identifier},
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestRemoveVariable:
    def test_with_valid_ids(self, client_with_referer, basket_variable):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable.basket.user)
        url = reverse(
            "workspace:remove_variable",
            kwargs={
                "basket_id": basket_variable.basket_id,
                "variable_id": basket_variable.variable_id,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_basket_id(self, client_with_referer, basket_variable):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable.basket.user)
        url = reverse(
            "workspace:remove_variable",
            kwargs={"basket_id": 999, "variable_id": basket_variable.variable_id},
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()

    def test_with_invalid_variable_id(
        self, client_with_referer, basket_variable, uuid_identifier
    ):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable.basket.user)
        url = reverse(
            "workspace:add_variable",
            kwargs={
                "basket_id": basket_variable.basket_id,
                "variable_id": uuid_identifier,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()


class TestAddConcept:
    def test_with_valid_ids(self, client_with_referer, basket, variable_with_concept):
        assert 0 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_concept",
            kwargs={
                "basket_id": basket.id,
                "concept_id": variable_with_concept.concept_id,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert variable_with_concept == basket_variable.variable
        assert basket == basket_variable.basket

    def test_with_invalid_basket_id(self, client_with_referer, variable_with_concept):
        assert 0 == BasketVariable.objects.count()
        client_with_referer.login(username="some-user", password="some-password")  # nosec
        url = reverse(
            "workspace:add_concept",
            kwargs={"basket_id": 999, "concept_id": variable_with_concept.concept_id},
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_concept_id(self, client_with_referer, basket, uuid_identifier):
        assert 0 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket.user)
        url = reverse(
            "workspace:add_concept",
            kwargs={"basket_id": basket.id, "concept_id": uuid_identifier},
        )
        response = client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()


class TestRemoveConcept:
    def test_with_valid_ids(self, client_with_referer, basket_variable_with_concept):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable_with_concept.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": basket_variable_with_concept.basket_id,
                "concept_id": basket_variable_with_concept.variable.concept_id,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == BasketVariable.objects.count()

    def test_with_invalid_basket_id(
        self, client_with_referer, basket_variable_with_concept
    ):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable_with_concept.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": 999,
                "concept_id": basket_variable_with_concept.variable.concept_id,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()

    def test_with_invalid_concept_id(
        self, client_with_referer, basket_variable_with_concept, uuid_identifier
    ):
        assert 1 == BasketVariable.objects.count()
        client_with_referer.force_login(user=basket_variable_with_concept.basket.user)
        url = reverse(
            "workspace:remove_concept",
            kwargs={
                "basket_id": basket_variable_with_concept.basket_id,
                "concept_id": uuid_identifier,
            },
        )
        response = client_with_referer.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code
        assert 1 == BasketVariable.objects.count()


class TestBasketToCsv:
    def test_with_valid_id(self, client, basket_variable):
        assert 1 == BasketVariable.objects.count()
        client.force_login(user=basket_variable.basket.user)
        url = reverse(
            "workspace:basket_to_csv", kwargs={"basket_id": basket_variable.basket_id}
        )
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code
        expected_content_type = "text/csv"
        assert expected_content_type == response["content-type"]
        content = response.content.decode("utf-8")
        expected_content_disposition = 'attachment; filename="basket.csv"'
        assert expected_content_disposition == response["Content-Disposition"]

        # test exported csv
        reader = csv.DictReader(content.splitlines())
        row = next(reader)
        assert basket_variable.variable.name == row["name"]
        assert basket_variable.variable.dataset.name == row["dataset_name"]
        assert basket_variable.variable.dataset.study.name == row["study_name"]
        assert basket_variable.variable.dataset.period.name == row["period_name"]

    def test_with_invalid_id(self, client, basket_variable):
        client.force_login(user=basket_variable.basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": 999})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestBasketDetail:
    def test_with_valid_id(self, client, basket):
        client.force_login(user=basket.user)
        url = reverse("workspace:basket_detail", kwargs={"basket_id": basket.id})
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_with_invalid_id(self, client, basket):
        client.force_login(user=basket.user)
        url = reverse("workspace:basket_detail", kwargs={"basket_id": 999})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestBasketSearch:
    def test_with_valid_id(self, client, basket):
        client.force_login(user=basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": basket.id})
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_with_invalid_id(self, client, basket):
        client.force_login(user=basket.user)
        url = reverse("workspace:basket_to_csv", kwargs={"basket_id": 999})
        response = client.get(url)
        assert status.HTTP_404_NOT_FOUND == response.status_code


class TestUserDelete:
    def test_with_valid_user(self, client, user):
        assert 1 == User.objects.count()
        client.force_login(user=user)
        url = reverse("workspace:user_delete")
        response = client.get(url)
        assert status.HTTP_302_FOUND == response.status_code
        assert 0 == User.objects.count()

    # TODO: you cannot delete an anonymous user -> NotImplementedError
    # @pytest.mark.django_db
    # def test_with_anonymous_user(self, client):
    #     assert 0 == User.objects.count()
    #     url = reverse("workspace:user_delete")
    #     response = client.get(url)
    #     assert status.HTTP_404_NOT_FOUND == response.status_code

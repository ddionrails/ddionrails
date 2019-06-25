# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for views in ddionrails.workspace app """

import pytest
from django.urls import reverse

from ddionrails.workspace.models import Basket
from tests import status

from .factories import UserFactory


class TestOwnBasketOnlyDecorator:
    def test_basket_belongs_to_user(self, client, basket):
        url = reverse("workspace:basket", kwargs={"basket_id": basket.id})
        client.login(username=basket.user, password="some-password")  # nosec
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code

    def test_basket_belongs_to_other_user(self, client, basket):
        other_user = UserFactory(username="other-user")
        basket.user = other_user
        basket.save()
        url = reverse("workspace:basket", kwargs={"basket_id": basket.id})
        client.login(username=basket.user, password="some-password")  # nosec
        response = client.get(url)
        assert status.HTTP_403_FORBIDDEN == response.status_code

    @pytest.mark.django_db
    def test_basket_does_not_exist(self, client):
        url = reverse("workspace:basket", kwargs={"basket_id": 1})
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
        # ignore B106: hardcoded_password_funcarg
        client.login(username="some-user", password="some-password")  # nosec
        url = reverse("workspace:account_overview")
        response = client.get(url)
        assert status.HTTP_200_OK == response.status_code


class TestBasketList:
    def test_basket_list_anonymous_user(self, client, basket):
        response = client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = []
        basket_list = response.context["basket_list"]
        assert expected == basket_list

    def test_basket_list_authenticated_user(self, client, basket):
        assert 1 == Basket.objects.count()
        client.login(username="some-user", password="some-password")  # nosec
        response = client.get("/workspace/baskets/")
        assert status.HTTP_200_OK == response.status_code
        expected = list(Basket.objects.all())
        basket_list = response.context["basket_list"]
        assert expected == list(basket_list)

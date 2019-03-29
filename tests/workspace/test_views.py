import pytest
from django.urls import reverse

from workspace.views import own_basket_only, script_detail

from .factories import UserFactory


class TestOwnBasketOnlyDecorator:
    def test_basket_belongs_to_user(self, mocker, basket):
        pass

    def test_basket_belongs_to_other_user(self, client, basket):
        other_user = UserFactory(username="other-user")
        pass

    def test_basket_does_not_exist(self, client, basket):
        pass


class TestScriptDetailView:
    @pytest.mark.skip
    def test_script_detail_view_with_script_created_before_update(
        self, rf, basket, script
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

        request = rf.get("script_detail", basket_id=basket.id, script_id=script.id)
        response = script_detail(request, basket.id, script.id)
        assert response.status_code == 200


class TestAccountOverview:
    def test_account_overview_anonymous_user(self, client):
        url = reverse("workspace:account_overview")
        response = client.get(url)
        assert response.status_code == 401

    def test_account_overview_authenticated_user(self, client, user):
        client.login(username="some-user", password="some-password")
        url = reverse("workspace:account_overview")
        response = client.get(url)
        assert response.status_code == 200


class TestBasketList:
    def test_basket_list_anonymous_user(self, db, client):
        pass

    def test_basket_list_authenticated_user(self):
        pass


class TestRenderScript:
    pass


class TestAddVariable:
    pass


class TestRemoveVariable:
    pass


class TestAddConcept:
    pass


class TestRemoveConcept:
    pass


class TestBasketCsv:
    pass


class TestBasketDetail:
    pass


class TestRegister:
    pass

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for forms in ddionrails.workspace app """

import pytest

from ddionrails.workspace.forms import BasketForm, UserCreationForm

pytestmark = [pytest.mark.workspace, pytest.mark.forms]  # pylint: disable=invalid-name


@pytest.fixture
def valid_basket_data(study, user):
    """ A valid input for basket forms and imports, relates to study and user fixture """
    return dict(name="some-basket", study=study.pk, user=user.pk)


@pytest.fixture
def invalid_basket_csv_data():
    """ An invalid input for basket forms and imports """
    return dict(name="some-basket")


@pytest.fixture
def valid_user_data():
    """ A valid input for user forms and imports """
    # ignore B106: hardcoded_password_funcarg
    return dict(username="some-user", password="some-password")  # nosec


@pytest.fixture
def valid_user_creation_data():
    """ A valid input for user creation forms and imports """
    return dict(
        username="some-user", password1="some-password", password2="some-password"
    )


class TestBasketForm:
    def test_form_with_invalid_data(self, empty_data):
        form = BasketForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
            "user": ["This field is required."],
        }
        assert form.errors == expected_errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_basket_data):
        form = BasketForm(data=valid_basket_data)
        expected = True
        assert expected is form.is_valid()


class TestUserCreationForm:
    def test_form_with_invalid_data(self, empty_data):
        form = UserCreationForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
        }
        assert expected_errors == form.errors

    @pytest.mark.django_db
    def test_form_with_valid_data(self, valid_user_creation_data):
        form = UserCreationForm(data=valid_user_creation_data)
        expected = True
        assert expected is form.is_valid()

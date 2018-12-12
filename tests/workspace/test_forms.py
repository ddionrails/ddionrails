import pytest

from workspace.forms import (
    BasketCSVForm,
    BasketForm,
    BasketVariableForm,
    UserCreationForm,
    UserForm,
)


pytestmark = [pytest.mark.workspace, pytest.mark.form]


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
    return dict(username="some-user", password="some-password")  # noqa


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

    def test_form_with_valid_data(self, db, valid_basket_data):
        form = BasketForm(data=valid_basket_data)
        assert form.is_valid() is True


class TestBasketCSVForm:
    def test_form_with_invalid_data(self, study, user):
        invalid_basket_csv_data = dict(
            name="", study_name=study.name, username=user.username
        )
        form = BasketCSVForm(data=invalid_basket_csv_data)
        assert form.is_valid() is False
        expected_errors = {"name": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data_other_keys(self, study, user):
        valid_basket_csv_data = dict(name="some-basket", study=study.pk, user=user.pk)
        form = BasketCSVForm(data=valid_basket_csv_data)
        assert form.is_valid() is True
        basket = form.save()
        assert basket.study == study
        assert basket.user == user

    def test_form_with_valid_data(self, study, user):
        valid_basket_csv_data = dict(
            name="some-basket", study_name=study.name, username=user.username
        )
        form = BasketCSVForm(data=valid_basket_csv_data)
        assert form.is_valid() is True

    def test_form_with_valid_data_not_lower_case(self, study, user):
        valid_basket_csv_data = dict(
            name="SOME-BASKET", study_name=study.name, username=user.username
        )
        form = BasketCSVForm(data=valid_basket_csv_data)
        assert form.is_valid() is True
        form.full_clean()
        assert form.data["name"] == "some-basket"
        assert form.data["cs_name"] == "SOME-BASKET"


class TestBasketVariableForm:
    def test_form_with_invalid_data(self, db, variable):
        invalid_basket_variable_data = dict(basket="", variable=variable.pk)
        form = BasketVariableForm(data=invalid_basket_variable_data)
        assert form.is_valid() is False
        expected_errors = {"basket": ["This field is required."]}
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, basket, variable):
        valid_basket_variable_data = dict(basket=basket.pk, variable=variable.pk)
        form = BasketVariableForm(data=valid_basket_variable_data)
        assert form.is_valid() is True
        basket_variable = form.save()
        assert basket_variable.basket == basket
        assert basket_variable.variable == variable

    def test_form_with_valid_data_other_keys(self, basket, variable):
        valid_basket_variable_data = dict(
            basket=basket.pk,
            study_name=variable.dataset.study.name,
            dataset_name=variable.dataset.name,
            variable_name=variable.name,
        )
        form = BasketVariableForm(data=valid_basket_variable_data)
        assert form.is_valid() is True
        basket_variable = form.save()
        assert basket_variable.basket == basket
        assert basket_variable.variable == variable

    def test_form_with_valid_data_with_basket_name(self, basket, variable):
        valid_basket_variable_data = dict(
            basket_name=basket.name,
            username=basket.user.username,
            study_name=variable.dataset.study.name,
            dataset_name=variable.dataset.name,
            variable_name=variable.name,
        )
        form = BasketVariableForm(data=valid_basket_variable_data)
        assert form.is_valid() is True
        basket_variable = form.save()
        assert basket_variable.basket == basket
        assert basket_variable.variable == variable

    def test_form_with_invalid_data_without_variable(self, basket):
        invalid_basket_variable_data = dict(basket=basket.pk)
        form = BasketVariableForm(data=invalid_basket_variable_data)
        assert form.data["basket"] == basket.pk
        assert form.data["variable"] is None


class TestUserCreationForm:
    def test_form_with_invalid_data(self, empty_data):
        form = UserCreationForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
        }
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, db, valid_user_creation_data):
        form = UserCreationForm(data=valid_user_creation_data)
        assert form.is_valid() is True


class TestUserForm:
    def test_form_with_invalid_data(self, empty_data):
        form = UserForm(data=empty_data)
        assert form.is_valid() is False
        expected_errors = {
            "username": ["This field is required."],
            "password": ["This field is required."],
        }
        assert form.errors == expected_errors

    def test_form_with_valid_data(self, db, valid_user_data):
        form = UserForm(data=valid_user_data)
        assert form.is_valid() is True

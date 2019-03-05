import pytest

from workspace.forms import BasketForm, UserCreationForm

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

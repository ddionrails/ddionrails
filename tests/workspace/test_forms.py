# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

"""Test cases for forms in ddionrails.workspace app"""

from django.test import TestCase

from ddionrails.workspace.forms import BasketForm, UserCreationForm
from tests.file_factories import FAKE
from tests.model_factories import StudyFactory, UserFactory


class TestBasketForm(TestCase):
    def test_form_with_invalid_data(self):
        form = BasketForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "name": ["This field is required."],
            "study": ["This field is required."],
            "user": ["This field is required."],
        }
        assert form.errors == expected_errors

    def test_form_with_valid_data(self):
        study = StudyFactory()
        user = UserFactory()
        form = BasketForm(data={"name": FAKE.word(), "study": study.pk, "user": user.pk})
        expected = True
        assert expected is form.is_valid()


class TestUserCreationForm(TestCase):
    def test_form_with_invalid_data(self):
        form = UserCreationForm(data={})
        assert form.is_valid() is False
        expected_errors = {
            "username": ["This field is required."],
            "password1": ["This field is required."],
            "password2": ["This field is required."],
        }
        self.assertEqual(expected_errors, form.errors)

    def test_form_with_valid_data(self):
        password = FAKE.password()
        form = UserCreationForm(
            data={
                "username": FAKE.user_name(),
                "password1": password,
                "password2": password,
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_password(self):
        password = FAKE.password()
        other_password = FAKE.password()
        while password == other_password:
            other_password = FAKE.password()
        form = UserCreationForm(
            data={
                "username": FAKE.user_name(),
                "password1": password,
                "password2": other_password,
            }
        )
        self.assertEqual(
            {"password2": ["The two password fields didn’t match."]}, form.errors
        )

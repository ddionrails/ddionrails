# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for pavement tasks in ddionrails project """

import pytest

from pavement import (
    create_admin,
    django_setup,
    docu,
    erd,
    full_docu,
    functional_test,
    migrate,
    reset_migrations,
    test,
)


@pytest.fixture
def mocked_sh(mocker):
    return mocker.patch("pavement.sh")


@pytest.fixture
def mocked_django_setup(mocker):
    return mocker.patch("django.setup")


@pytest.fixture
def mocked_django_management(mocker):
    return mocker.patch("django.core.management")


def test_docu_task(mocked_sh):
    docu()
    mocked_sh.assert_called_once_with("cd ../docs; make html")


def test_full_docu_task(mocked_sh):
    full_docu()
    mocked_sh.assert_called_once_with("cd ../docs; rm -r _build; make html")


def test_django_setup(mocked_django_setup):
    django_setup()
    mocked_django_setup.assert_called_once()


def test_create_admin():
    pass


def test_erd():
    pass


def test_migrate():
    pass


def test_test():
    pass


def test_functional_test():
    pass

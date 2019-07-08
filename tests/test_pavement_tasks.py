# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for pavement tasks in ddionrails project """

from unittest.mock import call

import pytest

from pavement import (
    create_admin,
    django_setup,
    docu,
    erd,
    full_docu,
    migrate,
    reset_migrations,
)


@pytest.fixture
def mocked_sh(mocker):
    return mocker.patch("pavement.sh")


@pytest.fixture
def mocked_django_setup(mocker):
    return mocker.patch("django.setup")


@pytest.fixture
def mocked_call_command(mocker):
    return mocker.patch("django.core.management.call_command")


def test_docu_task(mocked_sh):
    docu()
    mocked_sh.assert_called_once_with("cd ../docs; make html")


def test_full_docu_task(mocked_sh):
    full_docu()
    mocked_sh.assert_called_once_with("cd ../docs; rm -r _build; make html")


def test_django_setup(mocked_django_setup):
    django_setup()
    mocked_django_setup.assert_called_once()


@pytest.mark.django_db
def test_create_admin():
    from django.contrib.auth.models import User

    assert 0 == User.objects.count()
    assert ["django_setup"] == create_admin.needs
    # remove django_setup from needs for testing purposes
    create_admin.needs = []
    create_admin()
    assert 1 == User.objects.count()
    admin = User.objects.first()
    assert "admin" == admin.username


@pytest.mark.django_db
def test_reset_migrations(mocker, mocked_call_command):
    assert ["django_setup"] == reset_migrations.needs
    reset_migrations.needs = []
    mocked_unlink = mocker.patch("pathlib.PosixPath.unlink")
    reset_migrations()
    mocked_call_command.assert_called_once_with("makemigrations")
    mocked_unlink.assert_called()


@pytest.mark.django_db
def test_erd(mocked_call_command):
    assert ["django_setup"] == erd.needs
    erd.needs = []
    erd()
    mocked_call_command.assert_called_once_with(
        "graph_models", all_applications=True, outputfile="local/erd.png"
    )


@pytest.mark.django_db
def test_migrate(mocked_call_command):
    assert ["django_setup"] == migrate.needs
    migrate.needs = []
    migrate()
    assert [call("makemigrations"), call("migrate")] == mocked_call_command.call_args_list

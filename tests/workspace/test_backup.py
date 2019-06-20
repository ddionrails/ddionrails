# -*- coding: utf-8 -*-

""" Test cases for "python manage.py backup" """

import pytest
import tablib
from click.testing import CliRunner
from dateutil.parser import parse
from django.contrib.auth.models import User
from django.utils import timezone

from ddionrails.data.models import Variable
from ddionrails.workspace.management.commands import restore
from ddionrails.workspace.models import Basket, BasketVariable, Script
from ddionrails.workspace.resources import (
    BasketResource,
    BasketVariableExportResource,
    BasketVariableImportResource,
    ScriptExportResource,
    ScriptImportResource,
    UserResource,
)

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


class TestUserResource:
    def test_export(self, user):
        dataset = UserResource().export()
        assert user.username == dataset["username"][0]
        assert user.email == dataset["email"][0]
        assert user.password == dataset["password"][0]

    def test_import(self):
        assert 0 == User.objects.count()
        now = timezone.now()
        username = "some-user"
        email = "some-email@some-mail.org"
        password = "md5$salt$hashed-password"  # nosec
        dataset = tablib.Dataset(
            [username, email, password, now],
            headers=["username", "email", "password", "date_joined"],
        )

        result = UserResource().import_data(dataset, dry_run=False)
        assert False is result.has_errors()
        assert 1 == User.objects.count()

        user = User.objects.first()
        assert username == user.username
        assert email == user.email
        assert password == user.password
        assert now == user.date_joined


class TestBasketResource:
    def test_export(self, basket):
        dataset = BasketResource().export()

        # select first row from exported baskets
        basket_export = dataset.dict[0]
        assert basket.name in basket_export["name"]
        assert basket.label in basket_export["label"]
        assert basket.description in basket_export["description"]
        assert basket.study.name in basket_export["study"]
        assert basket.user.username in basket_export["user"]

        created_timestamp = basket.created.strftime("%Y-%m-%d %H:%M:%S %Z")
        assert created_timestamp in basket_export["created"]
        modified_timestamp = basket.modified.strftime("%Y-%m-%d %H:%M:%S %Z")
        assert modified_timestamp in basket_export["modified"]

    def test_import(self, user, study):
        assert 0 == Basket.objects.count()

        study = study.name
        username = user.username
        name = "some-basket"
        label = "Some basket"
        description = "This is some basket"
        created = "2019-03-10 12:00:00 UTC"
        created_datetime = parse(created)
        modified = "2019-03-10 12:00:00 UTC"

        dataset = tablib.Dataset(
            [study, username, name, label, description, created, modified],
            headers=[
                "study",
                "user",
                "name",
                "label",
                "description",
                "created",
                "modified",
            ],
        )

        result = BasketResource().import_data(dataset, dry_run=False)
        assert False is result.has_errors()
        assert 1 == Basket.objects.count()

        basket = Basket.objects.first()
        assert user == basket.user
        assert name == basket.name
        assert label == basket.label
        assert description == basket.description

        assert created_datetime == basket.created
        # Basket gets new modified timestamp after importing


class TestBasketVariableResource:
    def test_export(self, variable, basket):
        assert 0 == BasketVariable.objects.count()
        basket_variable = BasketVariable(basket=basket, variable=variable)
        basket_variable.save()

        dataset = BasketVariableExportResource().export()
        assert basket.name == dataset["basket"][0]
        assert basket.user.username == dataset["user"][0]
        assert basket.study.name == dataset["study"][0]
        assert variable.dataset.name == dataset["dataset"][0]
        assert variable.name == dataset["variable"][0]

    def test_import(self, db, basket, variable):
        assert 0 == BasketVariable.objects.count()
        assert 1 == Variable.objects.count()
        assert 1 == Basket.objects.count()
        assert 1 == User.objects.count()

        username = basket.user.username
        basket_name = basket.name
        study_name = variable.dataset.study.name
        dataset_name = variable.dataset.name
        variable_name = variable.name

        dataset = tablib.Dataset(
            [basket_name, username, study_name, dataset_name, variable_name],
            headers=["basket", "user", "study", "dataset", "variable"],
        )
        result = BasketVariableImportResource().import_data(dataset, dry_run=False)
        assert (
            False is result.has_errors()
        ), "Did not import basket variable without errors"
        assert 1 == BasketVariable.objects.count()
        basket_variable = BasketVariable.objects.first()
        assert basket == basket_variable.basket
        assert variable == basket_variable.variable


class TestScriptResource:
    def test_export(self, script):
        dataset = ScriptExportResource().export()
        assert script.basket.user.username == dataset["user"][0]
        assert script.basket.name == dataset["basket"][0]
        assert script.name == dataset["name"][0]
        assert script.generator_name == dataset["generator_name"][0]
        assert script.label == dataset["label"][0]
        assert script.settings == dataset["settings"][0]

    def test_import(self, study, basket):
        assert 0 == Script.objects.count()
        username = basket.user.username
        script_name = "some-script"
        generator_name = "some-generator-name"
        label = "Some script"
        settings = '{"some-key": "some-value"}'

        dataset = tablib.Dataset(
            [
                username,
                basket.name,
                study.name,
                script_name,
                generator_name,
                label,
                settings,
            ],
            headers=[
                "user",
                "basket",
                "study",
                "name",
                "generator_name",
                "label",
                "settings",
            ],
        )
        result = ScriptImportResource().import_data(dataset, dry_run=False)

        assert False is result.has_errors()
        assert 1 == Script.objects.count()
        script = Script.objects.first()
        assert script_name == script.name
        assert basket == script.basket
        assert study == script.basket.study
        assert generator_name == script.generator_name
        assert label == script.label
        assert settings == script.settings


@pytest.fixture()
def clirunner():
    return CliRunner()


class TestBackupManagementCommand:
    @pytest.mark.parametrize("argument", ("--users", "-u"))
    def test_backup_users(self, clirunner, argument, user):
        pass

    @pytest.mark.parametrize("argument", ("--baskets", "-b"))
    def test_backup_baskets(self, clirunner, argument):
        pass

    def test_backup_scripts(self):
        pass

    def test_backup_basket_variables(self):
        pass

    def test_backup_all(self):
        pass


class TestRestoreManagementCommand:
    @pytest.mark.parametrize("argument", ("--users", "-u"))
    def test_restore_users(self, clirunner, argument, client):
        assert 0 == User.objects.count()
        result = clirunner.invoke(
            restore.command, [argument, "-p", "tests/workspace/test_data/"]
        )
        assert result.exit_code == 0
        assert "Succesfully" in result.output
        assert 1 == User.objects.count()
        user = User.objects.first()
        assert "some-user" == user.username
        assert "some-user@some-mail.org" == user.email

        # test user can login
        logged_in = client.login(
            username=user.username, password="some-password"
        )  # nosec
        assert logged_in is True

    @pytest.mark.parametrize("argument", ("--baskets", "-b"))
    def test_restore_baskets(self, clirunner, argument, user, study):
        assert 0 == Basket.objects.count()
        result = clirunner.invoke(
            restore.command, [argument, "-p", "tests/workspace/test_data/"]
        )
        assert result.exit_code == 0
        assert "Succesfully" in result.output
        assert 1 == Basket.objects.count()
        basket = Basket.objects.first()
        assert "some-basket" == basket.name
        assert "Some Basket" == basket.label
        assert "This is some basket" == basket.description
        assert user == basket.user
        assert study == basket.study

    def test_restore_scripts(self):
        pass

    def test_restore_basket_variables(self):
        pass

    def test_restore_all(self):
        pass

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for "python manage.py backup" """

import csv
import shutil
import unittest
from pathlib import Path
from tempfile import mkdtemp

import pytest
import tablib
from _pytest.capture import CaptureFixture
from click.testing import CliRunner
from dateutil.parser import parse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone

from ddionrails.data.models import Variable
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

TEST_CASE = unittest.TestCase()


class TestUserResource:
    def test_export(self, user):
        dataset = UserResource().export()
        TEST_CASE.assertEqual(user.username, dataset["username"][0])
        TEST_CASE.assertEqual(user.email, dataset["email"][0])
        TEST_CASE.assertEqual(user.password, dataset["password"][0])

    def test_import(self):
        TEST_CASE.assertEqual(0, User.objects.count())
        now = timezone.now()
        username = "some-user"
        email = "some-email@some-mail.org"
        password = "md5$salt$hashed-password"  # nosec
        dataset = tablib.Dataset(
            [username, email, password, now],
            headers=["username", "email", "password", "date_joined"],
        )

        result = UserResource().import_data(dataset, dry_run=False)
        TEST_CASE.assertFalse(result.has_errors())
        TEST_CASE.assertEqual(1, User.objects.count())

        user = User.objects.first()
        TEST_CASE.assertEqual(username, user.username)
        TEST_CASE.assertEqual(email, user.email)
        TEST_CASE.assertEqual(password, user.password)
        TEST_CASE.assertEqual(now, user.date_joined)


class TestBasketResource:
    def test_export(self, basket):
        dataset = BasketResource().export()

        # select first row from exported baskets
        basket_export = dataset.dict[0]
        TEST_CASE.assertIn(basket.name, basket_export["name"])
        TEST_CASE.assertIn(basket.label, basket_export["label"])
        TEST_CASE.assertIn(basket.description, basket_export["description"])
        TEST_CASE.assertIn(basket.study.name, basket_export["study"])
        TEST_CASE.assertIn(basket.user.username, basket_export["user"])

        created_timestamp = basket.created.strftime("%Y-%m-%d %H:%M:%S %Z")
        TEST_CASE.assertIn(created_timestamp, basket_export["created"])
        modified_timestamp = basket.modified.strftime("%Y-%m-%d %H:%M:%S %Z")
        TEST_CASE.assertIn(modified_timestamp, basket_export["modified"])

    def test_import(self, user, study):
        TEST_CASE.assertEqual(0, Basket.objects.count())

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
        TEST_CASE.assertFalse(result.has_errors())
        TEST_CASE.assertEqual(1, Basket.objects.count())

        basket = Basket.objects.first()
        TEST_CASE.assertEqual(user, basket.user)
        TEST_CASE.assertEqual(name, basket.name)
        TEST_CASE.assertEqual(label, basket.label)
        TEST_CASE.assertEqual(description, basket.description)

        TEST_CASE.assertEqual(created_datetime, basket.created)
        # Basket gets new modified timestamp after importing


class TestBasketVariableResource:
    def test_export(self, variable, basket):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        basket_variable = BasketVariable(basket=basket, variable=variable)
        basket_variable.save()

        dataset = BasketVariableExportResource().export()
        TEST_CASE.assertEqual(basket.name, dataset["basket"][0])
        TEST_CASE.assertEqual(basket.user.username, dataset["user"][0])
        TEST_CASE.assertEqual(basket.study.name, dataset["study"][0])
        TEST_CASE.assertEqual(variable.dataset.name, dataset["dataset"][0])
        TEST_CASE.assertEqual(variable.name, dataset["variable"][0])

    def test_import(self, basket, variable):
        TEST_CASE.assertEqual(0, BasketVariable.objects.count())
        TEST_CASE.assertEqual(1, Variable.objects.count())
        TEST_CASE.assertEqual(1, Basket.objects.count())
        TEST_CASE.assertEqual(1, User.objects.count())

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
        TEST_CASE.assertFalse(result.has_errors())
        TEST_CASE.assertEqual(1, BasketVariable.objects.count())
        basket_variable = BasketVariable.objects.first()
        TEST_CASE.assertEqual(basket, basket_variable.basket)
        TEST_CASE.assertEqual(variable, basket_variable.variable)


class TestScriptResource:
    def test_export(self, script):
        dataset = ScriptExportResource().export()
        TEST_CASE.assertEqual(script.basket.user.username, dataset["user"][0])
        TEST_CASE.assertEqual(script.basket.name, dataset["basket"][0])
        TEST_CASE.assertEqual(script.name, dataset["name"][0])
        TEST_CASE.assertEqual(script.generator_name, dataset["generator_name"][0])
        TEST_CASE.assertEqual(script.label, dataset["label"][0])
        TEST_CASE.assertEqual(script.settings, dataset["settings"][0])

    def test_import(self, study, basket):
        TEST_CASE.assertEqual(0, Script.objects.count())
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

        TEST_CASE.assertFalse(result.has_errors())
        TEST_CASE.assertEqual(1, Script.objects.count())
        script = Script.objects.first()
        TEST_CASE.assertEqual(script_name, script.name)
        TEST_CASE.assertEqual(basket, script.basket)
        TEST_CASE.assertEqual(study, script.basket.study)
        TEST_CASE.assertEqual(generator_name, script.generator_name)
        TEST_CASE.assertEqual(label, script.label)
        TEST_CASE.assertEqual(settings, script.settings)


@pytest.fixture(name="clirunner")
def _clirunner():
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
    def test_restore_users(self, argument, client, capsys: CaptureFixture):
        TEST_CASE.assertEqual(0, User.objects.count())
        clear_password = "some-password"
        user = {
            "date_joined": "2019-01-01 10:00:00 UTC",
            "username": "some-user",
            "email": "some-user@some-mail.org",
            "password": make_password(clear_password),
        }
        tmp_folder = Path(mkdtemp())
        tmp_file = tmp_folder.joinpath("users.csv")
        with open(tmp_file, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=user.keys())
            writer.writeheader()
            writer.writerow(user)

        call_command("restore", argument, "-p", tmp_folder)

        shutil.rmtree(tmp_folder)

        TEST_CASE.assertIn("Successfully", capsys.readouterr().out)
        TEST_CASE.assertEqual(1, User.objects.count())

        user = User.objects.first()
        TEST_CASE.assertEqual("some-user", user.username)
        TEST_CASE.assertEqual("some-user@some-mail.org", user.email)

        # test user can login
        username = user.username
        password = "some-password"  # nosec
        logged_in = client.login(username=username, password=password)  # nosec
        TEST_CASE.assertTrue(logged_in)

    @pytest.mark.parametrize("argument", ("--baskets", "-b"))
    def test_restore_baskets(self, argument, user, study, capsys: CaptureFixture):
        TEST_CASE.assertEqual(0, Basket.objects.count())
        call_command("restore", argument, "-p", "tests/workspace/test_data/")
        TEST_CASE.assertIn("Successfully", capsys.readouterr().out)

        TEST_CASE.assertEqual(1, Basket.objects.count())

        basket = Basket.objects.first()
        TEST_CASE.assertEqual("some-basket", basket.name)
        TEST_CASE.assertEqual("Some Basket", basket.label)
        TEST_CASE.assertEqual("This is some basket", basket.description)
        TEST_CASE.assertEqual(user, basket.user)
        TEST_CASE.assertEqual(study, basket.study)

    def test_restore_scripts(self):
        pass

    def test_restore_basket_variables(self):
        pass

    def test_restore_all(self):
        pass

from django.contrib.auth.models import User
from django.utils import timezone

import tablib
from data.models import Variable
from workspace.models import Basket, BasketVariable, Script
from workspace.resources import (
    BasketResource,
    BasketVariableExportResource,
    BasketVariableImportResource,
    ScriptExportResource,
    ScriptImportResource,
    UserResource,
)


class TestUserResource:
    def test_export(self, db, user):
        dataset = UserResource().export()
        assert user.username == dataset["username"][0]
        assert user.email == dataset["email"][0]
        assert user.password == dataset["password"][0]
        # assert str(user.date_joined) == dataset["date_joined"][0]

    def test_import(self, db):
        assert 0 == User.objects.count()
        now = timezone.now()
        username = "some-user"
        email = "some-email@some-mail.org"
        password = "md5$salt$hashed-password"
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
    def test_export(self, db, basket):
        dataset = BasketResource().export()
        assert basket.name in dataset.csv
        assert basket.study.name in dataset.csv
        assert basket.user.username in dataset.csv

    def test_import(self, db, user, study):
        assert 0 == Basket.objects.count()

        study = study.name
        username = user.username
        name = "some-basket"
        label = "Some basket"
        description = "This is some basket"
        security_token = "some-security-token"

        dataset = tablib.Dataset(
            [study, username, name, label, description, security_token],
            headers=["study", "user", "name", "label", "description", "security_token"],
        )

        result = BasketResource().import_data(dataset, dry_run=False)
        assert False is result.has_errors()
        assert 1 == Basket.objects.count()

        basket = Basket.objects.first()
        assert user == basket.user
        assert name == basket.name
        assert label == basket.label
        assert description == basket.description
        assert security_token == basket.security_token


class TestBasketVariableResource:
    def test_export(self, db, variable, basket):
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
    def test_export(self, db, script):
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
            [username, basket.name, script_name, generator_name, label, settings],
            headers=["user", "basket", "name", "generator_name", "label", "settings"],
        )
        result = ScriptImportResource().import_data(dataset, dry_run=False)

        assert False is result.has_errors()
        assert 1 == Script.objects.count()
        script = Script.objects.first()
        assert script_name == script.name
        assert basket == script.basket
        assert generator_name == script.generator_name
        assert label == script.label
        assert settings == script.settings

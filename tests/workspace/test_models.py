# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for models in ddionrails.workspace app """

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from os import remove
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings

from ddionrails.concepts.models import Concept
from ddionrails.data.models import Dataset, Variable
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable, Script
from ddionrails.workspace.scripts import SoepStata
from tests.data.factories import DatasetFactory, VariableFactory
from tests.studies.factories import StudyFactory

pytestmark = [pytest.mark.workspace]

TEST_CASE = unittest.TestCase()


def csv_heading():
    return (
        "name,label,label_de,dataset_name,dataset_label,dataset_label_de,"
        "study_name,study_label,study_label_de,concept_name,period_name"
    )


@pytest.mark.usefixtures("basket", "study", "variable", "concept")
class TestBasketModel(LiveServerTestCase):
    basket: Basket
    concept: Concept
    study: Study
    variable: Variable
    tmp_dir: TemporaryDirectory

    def setUp(self) -> None:
        self.tmp_dir = TemporaryDirectory()
        return super().setUp()
    def tearDown(self) -> None:
        self.tmp_dir.cleanup()
        return super().tearDown()

    def test_string_method(self):
        expected = f"{self.basket.user.username}/{self.basket.name}"
        assert expected == str(self.basket)

    def test_absolute_url_method(self):
        expected = f"/workspace/baskets/{self.basket.id}"
        assert expected == self.basket.get_absolute_url()

    def test_html_description_method(self):
        with patch(
            "ddionrails.workspace.models.basket.render_markdown"
            ) as markdown_patch:
            self.basket.html_description()
            markdown_patch.assert_called_once()

    def test_title_method(self):
        assert self.basket.name == self.basket.title()

    def test_title_method_with_label(self):
        self.basket.label = "Some basket"
        assert self.basket.label == self.basket.title()

    def test_get_script_generators_method(self):
        result = self.basket.get_script_generators()
        expected = None
        assert expected is result

    def test_get_script_generators_method_with_config(self):
        # Set script_generators in study.config
        self.study.config = {"script_generators": "some-script-generator"}
        self.study.save()
        self.basket.refresh_from_db()
        result = self.basket.get_script_generators()
        expected = "some-script-generator"
        assert expected == result

    def test_to_csv_method_with_empty_basket(self):
        result = self.basket.to_csv()
        assert csv_heading() in result

    def test_to_csv_method_with_variable_in_basket(self):
        basket_variable = BasketVariable(basket=self.basket, variable=self.variable)
        basket_variable.save()
        result = self.basket.to_csv()
        assert csv_heading() in result
        assert self.variable.name in result
        assert self.variable.label in result
        assert self.variable.dataset.name in result
        assert self.variable.dataset.study.name in result

    def test_to_csv_method_with_variable_and_concept_in_basket(self):
        self.concept.variables.add(self.variable)
        basket_variable = BasketVariable(basket=self.basket, variable=self.variable)
        basket_variable.save()
        result = self.basket.to_csv()
        assert csv_heading() in result
        assert self.variable.name in result
        assert self.variable.label in result
        assert self.variable.dataset.name in result
        assert self.variable.dataset.study.name in result
        assert self.variable.concept.name in result

    def test_backup(self):
        @override_settings(BACKUP_DIR=Path(self.tmp_dir.name))
        def mock_backup_dir(instance):
            """Can we do a backup of existing Baskets."""
            instance.basket.save()
            basket_id = instance.basket.id
            basket_variable = BasketVariable(basket=instance.basket, variable=self.variable)
            other_variable = VariableFactory(name="test-variable")
            other_basket_variable = BasketVariable(basket=instance.basket, variable=other_variable)
            other_basket_variable.basket = instance.basket
            other_basket_variable.variable = other_variable
            basket_variable.save()
            other_basket_variable.save()

            backup_file = Basket.backup()

            instance.variable.delete()
            instance.basket.delete()

            call_command("loaddata", backup_file)

            instance.basket = Basket.objects.get(id=basket_id)
            basket_variables = list(instance.basket.variables.all())

            instance.assertIn(other_basket_variable.variable, basket_variables)
            instance.assertNotIn(basket_variable.variable, basket_variables)
            remove(backup_file)
        mock_backup_dir(self)

    def test_study_specific_backup(self):
        """Can we limit the backup to a specific study?"""
        @override_settings(BACKUP_DIR=Path(self.tmp_dir.name))
        def mock_backup_dir(instance):
            # A whole lot of boilerplate to set up another study basket.
            instance.basket.save()
            instance.basket.variables.add(self.variable)
            instance.basket.save()

            other_study = Study(name="other-sturdy")
            other_study.save()

            other_dataset = Dataset(name="other-dataset")
            other_dataset.study = other_study
            other_dataset.save()

            other_variable = Variable(name="other-variable")
            other_variable.dataset = other_dataset
            other_variable.save()

            other_basket = Basket(name="other-basket", study=other_study, user=instance.basket.user)
            other_basket.save()
            other_basket.variables.add(other_variable)
            other_basket.save()

            instance.assertTrue(BasketVariable.objects.get(variable=other_variable))
            instance.assertTrue(BasketVariable.objects.get(variable=instance.variable))

            # Actual testing
            backup_file = Basket.backup(study=instance.basket.study)
            BasketVariable.objects.all().delete()

            call_command("loaddata", backup_file)

            with instance.assertRaises(BasketVariable.DoesNotExist):
                BasketVariable.objects.get(variable=other_variable)

            instance.assertTrue(BasketVariable.objects.get(variable=instance.variable))
        mock_backup_dir(self)


@pytest.mark.usefixtures("study", "basket", "variable")
class TestBasketVariableModel(LiveServerTestCase):

    study: Study
    basket: Basket
    variable: Variable

    def test_clean_method(self):
        basket_variable = BasketVariable(
            basket_id=self.basket.id, variable_id=self.variable.id
        )
        basket_variable.clean()
        basket_variable.save()
        self.assertEqual(1, BasketVariable.objects.count())

    def test_clean_method_fails(self):
        """Ensure the correct error raising of the BasketVariable clean method.

        BasketVariable clean method should raise a ValidationError
        when basket and variable study do not match.
        """
        other_study = StudyFactory(name="some-other-study")
        other_dataset = DatasetFactory(name="some-other-dataset", study=other_study)
        other_variable = VariableFactory(
            name="some-other-variable", dataset=other_dataset
        )
        basket_variable = BasketVariable(
            basket_id=self.basket.id, variable_id=other_variable.id
        )
        with pytest.raises(ValidationError):
            basket_variable.clean()
        expected = 0
        self.assertEqual(expected, BasketVariable.objects.count())

    def test_remove_dangling_basket_variables(self):
        """Can we clean up BasketVariables, that link to non existing variables?"""
        basket_variable = BasketVariable(
            basket_id=self.basket.id, variable_id=self.variable.id
        )
        basket_variable.save()
        variable_id = basket_variable.variable.id
        basket_variable.variable.delete()
        basket_variable.clean_basket_variables()
        with self.assertRaises(BasketVariable.DoesNotExist):
            BasketVariable.objects.get(variable__id=variable_id)

    def test_remove_dangling_basket_variables_study_specific(self):
        """Can we clean up BasketVariables belonging to a specific study?"""
        other_study = StudyFactory(name="a_different_study")
        dataset = DatasetFactory(name="a_different_study")
        dataset.study = other_study
        dataset.save()
        new_variable = Variable()
        new_variable.name = "a_different_variable"
        new_variable.dataset = dataset
        basket_variable = BasketVariable(
            basket_id=self.basket.id, variable_id=self.variable.id
        )
        new_basket = Basket()
        new_basket.study = other_study
        new_basket.user = self.basket.user
        new_basket.save()
        new_basket_variable = BasketVariable()
        new_basket_variable.variable = new_variable
        new_basket_variable.basket = new_basket
        new_basket_variable.save()

        basket_variable.save()
        variable_id = basket_variable.variable.id
        basket_variable.variable.delete()
        new_variable.delete()
        basket_variable.clean_basket_variables(study_name=self.basket.study.name)
        with self.assertRaises(BasketVariable.DoesNotExist):
            BasketVariable.objects.get(variable__id=variable_id)


class TestScriptModel:
    @pytest.mark.usefixtures("db", "script_metadata")
    def test_get_config_method(self, script):
        result = script.get_config()
        assert isinstance(result, SoepStata)

    def test_get_config_method_with_local_config(self, script):
        script.local_config = "local-config"
        assert script.local_config == script.get_config()

    def test_get_settings_method(self, script):
        script.settings_dict = dict(key="value")
        result = script.get_settings()
        expected = "value"
        assert expected == result["key"]

    def test_get_settings_method_without_settings_dict(self, script):
        script.settings = '{"key": "value"}'
        result = script.get_settings()
        assert result["key"] == "value"

    def test_get_script_input_method(self, mocker, script):
        mocked_get_config = mocker.patch.object(Script, "get_config")
        script.get_script_input()
        mocked_get_config.assert_called_once()

    def test_title_method(self, script):
        script.label = ""
        assert script.name == script.title()

    def test_title_method_with_label(self, script):
        assert script.label == script.title()

    def test_string_method(self, script):
        expected = f"/workspace/baskets/{script.basket.id}/scripts/{script.id}"
        assert expected == str(script)

    def test_absolute_url_method(self, script):
        expected = f"/workspace/baskets/{script.basket.id}/scripts/{script.id}"
        assert expected == script.get_absolute_url()

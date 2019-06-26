# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,no-member,invalid-name

""" Test cases for mixins in ddionrails.base app """

import pathlib

import pytest
from django.db import models
from django.forms import ModelForm

import ddionrails.base
from ddionrails.base.mixins import AdminMixin, ImportPathMixin, ModelMixin
from ddionrails.concepts.models import Concept

pytestmark = [pytest.mark.ddionrails, pytest.mark.mixins]


class MixinChild(ModelMixin, models.Model):
    name = models.CharField()
    label = models.CharField()
    description = models.CharField()

    class Meta:
        app_label = "test"


class TestModelMixin:
    def test_get_or_create_method(self, mocker):
        with mocker.patch(
            "tests.base.test_mixins.MixinChild.objects.get_or_create", return_value=(1, 1)
        ):
            dictionary = dict(name="some-name")
            MixinChild.get_or_create(dictionary)
            MixinChild.objects.get_or_create.assert_called_once()

    def test_get_or_create_method_without_lower_strings(self, mocker):
        with mocker.patch(
            "tests.base.test_mixins.MixinChild.objects.get_or_create", return_value=(1, 1)
        ):
            dictionary = dict(name="SOME-NAME")
            MixinChild.get_or_create(dictionary, lower_strings=False)
            MixinChild.objects.get_or_create.assert_called_once()

    def test_get_method_success(self, mocker):
        with mocker.patch(
            "tests.base.test_mixins.MixinChild.objects.get", return_value=True
        ):
            dictionary = dict(name="some-name")
            obj = MixinChild.get(dictionary)
            assert obj is True

    @pytest.mark.django_db
    def test_get_method_failure(self):
        dictionary = dict(name="some-name")
        # This test case uses an actual subclass of ModelMixin
        obj = Concept.get(dictionary)
        assert obj is None

    def test_default_form_method(self):
        form = MixinChild.default_form()
        assert issubclass(form, ModelForm)
        assert list(form.base_fields.keys()) == ModelMixin.DOR.io_fields

    def test_to_dict_method(self):
        mixin = ModelMixin()
        mixin.name = "some-name"
        mixin.label = "some-label"
        mixin.description = "some-description"
        dictionary = mixin.to_dict()
        expected = dict(
            name="some-name", label="some-label", description="some-description"
        )
        assert dictionary == expected

    def test_title_method(self):
        mixin = ModelMixin()
        result = mixin.title()
        assert result is ""

    def test_title_method_with_name(self):
        mixin = ModelMixin()
        mixin.name = "some-name"
        assert mixin.title() is mixin.name

    def test_title_method_with_label(self):
        mixin = ModelMixin()
        mixin.label = "some-label"
        assert mixin.title() is mixin.label

    def test_html_description_method(self, mocker):

        with mocker.patch("ddionrails.base.mixins.render_markdown"):
            mixin = ModelMixin()
            mixin.description = "some-description"
            mixin.html_description()
            ddionrails.base.mixins.render_markdown.assert_called_once()

    def test_html_description_method_without_description(self):
        mixin = ModelMixin()
        result = mixin.html_description()
        assert result == ""

    def test_string_method_single_id_field(self):
        mixin = ModelMixin()
        mixin.name = "some-name"
        assert mixin.name == str(mixin)

    def test_string_method_multiple_id_field(self):
        mixin = ModelMixin()
        mixin.DOR.id_fields = ["id1", "id2"]
        mixin.id1 = "name-1"
        mixin.id2 = "name-2"
        expected = f"{mixin.id1}/{mixin.id2}"
        assert expected == str(mixin)


class TestImportPathMixin:
    def test_import_path_method(self, settings):
        mixin = ImportPathMixin()
        mixin.name = "name"
        result = mixin.import_path()
        expected = pathlib.Path(settings.IMPORT_REPO_PATH).joinpath(
            mixin.name, settings.IMPORT_SUB_DIRECTORY
        )
        assert expected == result


@pytest.fixture
def admin_mixin():
    """ An instantiated admin mixin"""
    return AdminMixin()


class TestAdminMixin:
    @staticmethod
    def test_study_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.study.name = "some-study"
        result = admin_mixin.study_name(obj)
        assert obj.study.name == result

    @staticmethod
    def test_study_name_without_study(admin_mixin, mocker):
        obj = mocker.Mock()
        # This object has no study attribute
        del obj.study
        result = admin_mixin.study_name(obj)
        assert None is result

    @staticmethod
    def test_period_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.period.name = "some-period"
        result = admin_mixin.period_name(obj)
        assert obj.period.name == result

    @staticmethod
    def test_period_name_without_period(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.period
        result = admin_mixin.period_name(obj)
        assert None is result

    @staticmethod
    def test_analysis_unit_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.analysis_unit.name = "some-analysis_unit"
        result = admin_mixin.analysis_unit_name(obj)
        assert obj.analysis_unit.name == result

    @staticmethod
    def test_analysis_unit_name_without_analysis_unit(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.analysis_unit
        result = admin_mixin.analysis_unit_name(obj)
        assert None is result

    @staticmethod
    def test_dataset_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.dataset.name = "some-dataset"
        result = admin_mixin.dataset_name(obj)
        assert obj.dataset.name == result

    @staticmethod
    def test_dataset_name_without_dataset(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.dataset
        result = admin_mixin.dataset_name(obj)
        assert None is result

    @staticmethod
    def test_dataset_study_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.dataset.study.name = "some-study"
        result = admin_mixin.dataset_study_name(obj)
        assert obj.dataset.study.name == result

    @staticmethod
    def test_dataset_study_name_without_study(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.dataset
        result = admin_mixin.dataset_study_name(obj)
        assert None is result

    @staticmethod
    def test_instrument_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.instrument.name = "some-instrument"
        result = admin_mixin.instrument_name(obj)
        assert obj.instrument.name == result

    @staticmethod
    def test_instrument_name_without_instrument(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.instrument
        result = admin_mixin.instrument_name(obj)
        assert None is result

    @staticmethod
    def test_instrument_study_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.instrument.study.name = "some-study"
        result = admin_mixin.instrument_study_name(obj)
        assert obj.instrument.study.name == result

    @staticmethod
    def test_instrument_study_name_without_instrument(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.instrument
        result = admin_mixin.instrument_study_name(obj)
        assert None is result

    @staticmethod
    def test_basket_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.basket.name = "some-basket"
        result = admin_mixin.basket_name(obj)
        assert obj.basket.name == result

    @staticmethod
    def test_basket_name_without_study(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.basket
        result = admin_mixin.basket_name(obj)
        assert None is result

    @staticmethod
    def test_basket_study_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.basket.study.name = "some-study"
        result = admin_mixin.basket_study_name(obj)
        assert obj.basket.study.name == result

    @staticmethod
    def test_basket_study_name_without_basket(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.basket
        result = admin_mixin.basket_study_name(obj)
        assert None is result

    @staticmethod
    def test_user_name(admin_mixin, mocker):
        obj = mocker.Mock()
        obj.basket.user.username = "some-user"
        result = admin_mixin.user_name(obj)
        assert obj.basket.user.username == result

    @staticmethod
    def test_user_name_without_user(admin_mixin, mocker):
        obj = mocker.Mock()
        del obj.basket
        result = admin_mixin.user_name(obj)
        assert None is result

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,no-member,invalid-name

""" Test cases for mixins in ddionrails.base app """


import pytest
from django.db import models
from django.forms import ModelForm

import ddionrails.base
from ddionrails.base.mixins import AdminMixin, ModelMixin
from ddionrails.concepts.models import Concept

pytestmark = [pytest.mark.ddionrails, pytest.mark.mixins]


@pytest.fixture(name="admin_mixin")
def _admin_mixin():
    """An instantiated AdminMixin"""
    return AdminMixin()


@pytest.fixture(name="model_mixin")
def _model_mixin():
    """An instantiated ModelMixin"""
    return ModelMixin()


class MixinChild(ModelMixin, models.Model):
    name = models.CharField()
    label = models.CharField()
    description = models.CharField()

    class Meta:
        app_label = "test"


class TestModelMixin:
    def test_get_method_success(self, mocker):
        mocker.patch("tests.base.test_mixins.MixinChild.objects.get", return_value=True)
        dictionary = {"name": "some-name"}
        result = MixinChild.get(dictionary)
        expected = True
        assert expected is result

    @pytest.mark.django_db
    def test_get_method_failure(self):
        dictionary = {"name": "some-name"}
        # This test case uses an actual subclass of ModelMixin
        result = Concept.get(dictionary)
        expected = None
        assert expected is result

    def test_default_form_method(self):
        form = MixinChild.default_form()
        assert issubclass(form, ModelForm)
        assert list(form.base_fields.keys()) == ModelMixin.DOR.io_fields

    def test_to_dict_method(self, model_mixin):
        model_mixin.name = "some-name"
        model_mixin.label = "some-label"
        model_mixin.description = "some-description"
        result = model_mixin.to_dict()
        expected = {
            "name": "some-name",
            "label": "some-label",
            "description": "some-description",
        }
        assert expected == result

    def test_title_method(self, model_mixin):
        result = model_mixin.title()
        expected = ""
        assert expected is result

    def test_title_method_with_name(self, model_mixin):
        model_mixin.name = "some-name"
        result = model_mixin.title()
        expected = model_mixin.name
        assert expected == result

    def test_title_method_with_label(self, model_mixin):
        model_mixin.label = "some-label"
        expected = model_mixin.label
        result = model_mixin.title()
        assert expected == result

    def test_set_language_method(self, model_mixin):
        model_mixin.set_language()
        expected = "en"
        result = model_mixin.language
        assert expected == result

    def test_set_language_method_de(self, model_mixin):
        model_mixin.set_language("de")
        expected = "de"
        result = model_mixin.language
        assert expected == result

    def test_set_language_method_unsupported_language(self, model_mixin):
        model_mixin.set_language("fr")
        expected = "en"
        result = model_mixin.language
        assert expected == result

    def test_html_description_method(self, mocker, model_mixin):
        mocker.patch("ddionrails.base.mixins.render_markdown")
        model_mixin.description = "some-description"
        model_mixin.html_description()
        ddionrails.base.mixins.render_markdown.assert_called_once()

    def test_html_description_method_without_description(self, model_mixin):
        result = model_mixin.html_description()
        expected = ""
        assert expected == result


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

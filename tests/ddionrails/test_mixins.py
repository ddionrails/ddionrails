import pytest
from django.db import models
from django.forms import ModelForm

import ddionrails
from concepts.models import Concept
from ddionrails.mixins import ModelMixin

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
            "tests.ddionrails.test_mixins.MixinChild.objects.get_or_create",
            return_value=(1, 1),
        ):
            dictionary = dict(name="some-name")
            MixinChild.get_or_create(dictionary)
            MixinChild.objects.get_or_create.assert_called_once()

    def test_get_or_create_method_without_lower_strings(self, mocker):
        with mocker.patch(
            "tests.ddionrails.test_mixins.MixinChild.objects.get_or_create",
            return_value=(1, 1),
        ):
            dictionary = dict(name="SOME-NAME")
            MixinChild.get_or_create(dictionary, lower_strings=False)
            MixinChild.objects.get_or_create.assert_called_once()

    def test_get_method_success(self, mocker):
        with mocker.patch(
            "tests.ddionrails.test_mixins.MixinChild.objects.get", return_value=True
        ):
            dictionary = dict(name="some-name")
            object = MixinChild.get(dictionary)
            assert object is True

    def test_get_method_failure(self, db):
        dictionary = dict(name="some-name")
        # TODO: Workaround with actual model. Remove this dependency
        object = Concept.get(dictionary)
        assert object is None

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

        with mocker.patch("ddionrails.mixins.render_markdown"):
            mixin = ModelMixin()
            mixin.description = "some-description"
            mixin.html_description()
            ddionrails.mixins.render_markdown.assert_called_once()

    def test_html_description_method_without_description(self, mocker):
        mixin = ModelMixin()
        result = mixin.html_description()
        assert result == ""

    def test_get_attribute_method(self):
        mixin = ModelMixin()
        mixin.name = "some-name"
        result = mixin.get_attribute("self.name")
        assert result == mixin.name

    def test_get_attribute_method_default(self):
        mixin = ModelMixin()
        result = mixin.get_attribute("self.name")
        assert result is None

    def test_string_id_method_single_id_field(self):
        mixin = ModelMixin()
        mixin.name = "some-name"
        assert mixin.string_id() == mixin.name

    def test_string_id_method_multiple_id_field(self):
        mixin = ModelMixin()
        mixin.DOR.id_fields = ["id1", "id2"]
        mixin.id1 = "name-1"
        mixin.id2 = "name-2"
        assert mixin.string_id() == mixin.id1 + "/" + mixin.id2

    def test_string_method(self, mocker):
        mixin = ModelMixin()
        with mocker.patch("ddionrails.mixins.ModelMixin.string_id", return_value=""):
            assert str(mixin) == ""
            mixin.string_id.assert_called_once()

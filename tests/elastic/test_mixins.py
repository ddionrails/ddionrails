# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for mixin in ddionrails.elastic app """

import json

from elasticsearch import Elasticsearch

from ddionrails.elastic.mixins import ModelMixin


class TestModelMixin:
    def test_get_elastic_method(self, mocker):
        mocked_es_get = mocker.patch.object(Elasticsearch, "get")
        model_mixin = ModelMixin()
        model_mixin.id = 1
        model_mixin.get_elastic()
        mocked_es_get.assert_called_once()

    def test_get_elastic_method_as_json(self):
        model_mixin = ModelMixin()
        model_mixin.elastic = dict(_id=1, status="not found")
        expected = json.dumps(model_mixin.elastic)
        result = model_mixin.get_elastic(as_json=True)
        assert result == expected

    def test_get_elastic_method_without_search(self):
        model_mixin = ModelMixin()
        model_mixin.elastic = dict(_id=1, status="not found")
        result = model_mixin.get_elastic()
        assert result == model_mixin.elastic

    def test_get_source_method(self, mocker):
        mocked_get_elastic = mocker.patch.object(ModelMixin, "get_elastic")
        mocked_get_elastic.return_value = dict(
            _id=1, _index="dor", _source=dict(name="some-variable")
        )
        model_mixin = ModelMixin()
        result = model_mixin.get_source()
        assert result["name"] == "some-variable"

    def test_get_source_method_as_json(self, mocker):
        mocked_get_elastic = mocker.patch.object(ModelMixin, "get_elastic")
        mocked_get_elastic.return_value = dict(
            _id=1, _index="dor", _source=dict(name="some-variable")
        )
        model_mixin = ModelMixin()
        result = model_mixin.get_source(as_json=True)
        assert result == json.dumps({"name": "some-variable"})

    def test_get_attribute_method(self, mocker):
        mocked_get_elastic = mocker.patch.object(ModelMixin, "get_elastic")
        mocked_get_elastic.return_value = dict(
            _id=1, _index="dor", _source=dict(name="some-variable")
        )
        model_mixin = ModelMixin()
        result = model_mixin.get_attribute("name", None)
        assert result == "some-variable"

    def test_get_attribute_method_fails(self, mocker):
        mocked_get_elastic = mocker.patch.object(ModelMixin, "get_elastic")
        mocked_get_elastic.return_value = dict(
            _id=1, _index="dor", _source=dict(name="some-variable")
        )
        model_mixin = ModelMixin()
        result = model_mixin.get_attribute("alternative", None)
        assert result is None

    def test_delete_elastic_method(self, mocker):
        mocked_es_delete = mocker.patch.object(Elasticsearch, "delete")
        model_mixin = ModelMixin()
        model_mixin.id = 1
        model_mixin.delete_elastic()
        mocked_es_delete.assert_called_once()

    def test_set_elastic_method(self, mocker):
        mocked_es_index = mocker.patch.object(Elasticsearch, "index")
        model_mixin = ModelMixin()
        model_mixin.id = 1
        model_mixin.set_elastic(body={"field": "value"})
        mocked_es_index.assert_called_once()

    def test_set_elastic_method_with_update(self, mocker):
        mocked_es_update = mocker.patch.object(Elasticsearch, "update")
        model_mixin = ModelMixin()
        model_mixin.id = 1
        result = model_mixin.set_elastic(body={"field": "updated-value"}, update=True)
        mocked_es_update.assert_called_once()

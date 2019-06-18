# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.elastic app """

from ddionrails.elastic.helpers import Hit


class TestHit:
    def test_init_method(self):
        json = dict(_id="1", _index="some-index", _score=1, _source=1, _type="some-type")
        hit = Hit(json)
        assert hit.id == json["_id"]
        assert hit.index == json["_index"]
        assert hit.score == json["_score"]
        assert hit.source == json["_source"]
        assert hit.type == json["_type"]
        assert hit.key == f"{json['_index']}/{json['_type']}/{json['_id']}"

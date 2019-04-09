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


class TestResult:
    def test_init_method(self):
        pass

    def test_parse_hits_methods(self):
        pass


class TestParseResults:
    pass


class TestSimpleSearch:
    pass

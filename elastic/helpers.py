from elasticsearch import Elasticsearch

def parse_results(results):
    """
    Transform results into a simplified strutured that can be used
    in Django's template language.
    """
    try:
        hits = results["hits"]["hits"]
        new_results = list()
        for hit in hits:
            x = hit["_source"].copy()
            x["type"] = hit["_type"]
            x["id"] = hit["_id"]
            new_results.append(x)
        return new_results
    except:
      return []

def simple_search(q, from_value=0, size_value=25):
    """Simple search for a term in all document types."""
    es = Elasticsearch()
    body = {
        "query": {"query_string": {"query": q}},
        "from": from_value,
        "size": size_value,
    }
    results = es.search(body=body)
    return results


class Hit:
    def __init__(self, json):
        self.json = json
        self.id = json["_id"]
        self.index = json["_index"]
        self.score = json["_score"]
        self.source = json["_source"]
        self.type = json["_type"]
        self.key = "/".join([
            self.index,
            self.type,
            self.id,
        ])


class Result:
    def __init__(self, json):
        self.json = json
        self.shards = json["_shards"]
        self._parse_hits(json["hits"]["hits"])

    def _parse_hits(self, json_hits):
        self.hits = dict()
        for json_hit in json_hits:
            hit = Hit(json_hit)
            self.hits[hit.key] = hit

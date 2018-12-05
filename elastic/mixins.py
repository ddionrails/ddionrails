import json
from elasticsearch import Elasticsearch
from django.conf import settings

es = Elasticsearch()

class ModelMixin:
    """
    Requires a valid DOC_TYPE
    """
    
    INDEX_NAME = settings.INDEX_NAME
    DOC_TYPE = "default"
    elastic = None

    def get_elastic(self, as_json=False):
        if not self.elastic:
            try:
                self.elastic= es.get(
                    index=self.INDEX_NAME,
                    doc_type=self.DOC_TYPE,
                    id=self.id,
                )
            except:
                self.elastic = {"_id": self.id, "status":"not found"}
        if as_json:
            return json.dumps(self.elastic)
        else:
            return self.elastic

    def get_source(self, as_json=False):
        elastic = self.get_elastic()
        source = elastic["_source"]
        if as_json:
            return json.dumps(source)
        else:
            return source

    def get_attribute(self, name, default):
        try:
            elastic = self.get_elastic()
            return elastic["_source"][name]
        except:
            return default

    def delete_elastic(self):
        es.delete(
            index=self.INDEX_NAME,
            doc_type=self.DOC_TYPE,
            id=self.id,
        )

    def set_elastic(self, body, update=False):
        """
        Re-index the document, unless ``update=True``. The update method
        supports update by doc only.
        """
        if update:
           res = es.update(
                index=self.INDEX_NAME ,
                doc_type=self.DOC_TYPE,
                id=self.id,
                body=dict(doc=body),
            )
        else:
            res = es.index(
                index=self.INDEX_NAME,
                doc_type=self.DOC_TYPE,
                id=self.id,
                body=body,
            )
        return res

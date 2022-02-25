""" Define base fields for all documents except ConceptDocument."""

# Use Any for typing because mypy does not recognize models as subtypes of ModelBase
from typing import Any, Dict

from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.analysis import tokenizer

from ddionrails.studies.models import Study

edge_ngram_completion = analyzer(
    "edge_ngram_completion",
    tokenizer=tokenizer("edge_ngram", "edge_ngram", min_gram=1, max_gram=10),
)


class GenericDocument(Document):
    """Base for search documents."""

    # attributes
    id = fields.TextField()
    name = fields.TextField(analyzer=edge_ngram_completion)
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")

    # relations as attributes
    study = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(),
            "label_de": fields.TextField(),
        }
    )
    study_name = fields.KeywordField()

    def prepare_study_name(self, model_object: Any) -> str:
        """Collect study title for facets."""
        study = self._get_study(model_object)
        return study.title()

    def prepare_study(self, model_object: Any) -> Dict[str, str]:
        """Collect study fields for indexing."""
        study = self._get_study(model_object)
        name = getattr(study, "name", "")
        return {
            "name": study.name,
            "label": getattr(study, "label", name),
            "label_de": getattr(study, "label_de", name),
        }

    @staticmethod
    def _get_study(model_object: Any) -> Study:
        raise NotImplementedError

    @staticmethod
    def _handle_missing_content(content: str) -> str:
        if content is None:
            return "Not Categorized"
        if str(content.title()).lower() in ["none", "unspecified"]:
            return "Not Categorized"
        return content.title()


class GenericDataDocument(GenericDocument):
    """Base for variable and question documents."""

    concept = fields.ObjectField(
        properties={
            "label": fields.TextField(analyzer="english"),
            "label_de": fields.TextField(analyzer="german"),
        }
    )

    # facets
    analysis_unit = fields.KeywordField()
    period = fields.KeywordField()

    @staticmethod
    def _get_study(model_object: Any) -> Study:
        raise NotImplementedError

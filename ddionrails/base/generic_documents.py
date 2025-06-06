""" Define base fields for all documents except ConceptDocument."""

# Use Any for typing because mypy does not recognize models as subtypes of ModelBase
from typing import Any, Dict

from django_elasticsearch_dsl import Document, fields
from elasticsearch.dsl import analyzer, tokenizer

from ddionrails.studies.models import Study

edge_ngram_completion = analyzer(
    "edge_ngram_completion",
    tokenizer=tokenizer("edge_ngram", "edge_ngram", min_gram=1, max_gram=10),
)


def prepare_model_name_and_labels(model) -> Dict[str, str]:
    """Prepare name and label data for indexing."""
    label_de = model.label_de
    label = model.label
    if not label_de:
        label_de = label
    if not label_de:
        label = model.name
        label_de = model.name

    return {"name": model.name, "label": label, "label_de": label_de}


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
    study_name_de = fields.KeywordField()

    def prepare_study_name(self, model_object: Any) -> str:
        """Collect study title for facets."""
        study = self._get_study(model_object)
        return study.label

    def prepare_study_name_de(self, model_object: Any) -> str:
        """Collect study title for facets."""
        study = self._get_study(model_object)
        label_de = study.label
        if study.label_de:
            label_de = study.label_de
        return label_de

    def prepare_study(self, model_object: Any) -> Dict[str, str]:
        """Collect study fields for indexing."""
        return prepare_model_name_and_labels(self._get_study(model_object))

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

    @staticmethod
    def _handle_missing_dict_content(content: "AnalysisUnit") -> dict[str, str]:
        output = {}
        if content is None:
            output["label"] = "Not Categorized"
            output["label_de"] = "Nicht Kategorisiert"
            return output
        if content.label is None or content.label.lower() in ["none", "unspecified", ""]:
            output["label"] = "Not Categorized"
        else:
            output["label"] = content.label

        if content.label_de is None or content.label_de.lower() in [
            "none",
            "unspecified",
            "",
        ]:
            output["label_de"] = "Nicht Kategorisiert"
        else:
            output["label_de"] = content.label_de
        return output


class GenericDataDocument(GenericDocument):
    """Base for variable and question documents."""

    concept = fields.ObjectField(
        properties={
            "label": fields.TextField(analyzer="english"),
            "label_de": fields.TextField(analyzer="german"),
        }
    )

    # facets
    analysis_unit = fields.ObjectField(
        properties={
            "label": fields.KeywordField(),
            "label_de": fields.KeywordField(),
        }
    )
    period = fields.ObjectField(
        properties={
            "label": fields.KeywordField(),
            "label_de": fields.KeywordField(),
        }
    )

    @staticmethod
    def _get_study(model_object: Any) -> Study:
        raise NotImplementedError

# -*- coding: utf-8 -*-

""" Search documents for indexing models from ddionrails.concepts app into Elasticsearch


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from typing import Any, List

from django.conf import settings
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.base.generic_documents import GenericDocument
from ddionrails.studies.models import Study

from .models import Concept, Topic


@registry.register_document
class ConceptDocument(Document):
    """Search document for concepts.Concept

    We do not inherit from GenericDocument since concepts can belong to
    several studies, which have to be handled differently.
    """

    # attributes
    name = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")

    # facets
    study_name = fields.ListField(fields.KeywordField())

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
        studies = Study.objects.filter(topics__concepts__id=model_object.id).distinct()
        names = ", ".join([study.title() for study in studies])
        if names:
            return names

        return "No study"

    def prepare_study_name_de(self, model_object: Any) -> str:
        """Collect study title for facets."""
        studies = Study.objects.filter(topics__concepts__id=model_object.id).distinct()
        name_list = []
        for study in studies:
            if not study.label_de:
                name_list.append(study.title())
                continue
            name_list.append(study.label_de)
        names = ", ".join(name_list)
        if names:
            return names

        return "Keine Studie"

    def prepare_study(self, model_object: Any) -> dict[str, str]:
        """Collect study fields for indexing."""
        studies = Study.objects.filter(topics__concepts__id=model_object.id).distinct()
        names = []
        labels = []
        labels_de = []
        for study in studies:
            name = study.name
            if not name:
                continue
            names.append(name)
            if study.label:
                labels.append(study.label)
            else:
                labels.append(name)
            if study.label_de:
                labels_de.append(study.label_de)
            else:
                labels_de.append(name)

        return {
            "name": ", ".join(names),
            "label": ", ".join(labels),
            "label_de": ", ".join(labels_de),
        }

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}concepts"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Concept
        queryset_pagination = 5000

    def get_queryset(self) -> Any:
        """
        Return the queryset that should be indexed by this doc type,
        with select related objects.
        """
        return (
            super()
            .get_queryset()
            .exclude(label=None)
            .prefetch_related("variables", "concepts_questions")
        )


@registry.register_document
class TopicDocument(GenericDocument):
    """Search document for concepts.Topic"""

    study = fields.ObjectField(
        properties={
            "name": fields.TextField(),
            "label": fields.TextField(),
            "label_de": fields.TextField(),
        }
    )

    @staticmethod
    def prepare_study_name(model_object: Topic) -> str:
        """Return the related study"""
        return model_object.study.title()

    def prepare_study(self, model_object: Any) -> dict[str, str]:
        """Collect study fields for indexing."""
        study = Study.objects.get(topics__id=model_object.id)
        return {
            "name": study.name,
            "label": study.label,
            "label_de": study.label_de,
        }

    @staticmethod
    def _get_study(model_object: Topic) -> Study:
        return model_object.study

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}topics"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Topic
        queryset_pagination = 5000  # TODO: Find out if this is the best fix

    def get_queryset(self) -> Any:
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

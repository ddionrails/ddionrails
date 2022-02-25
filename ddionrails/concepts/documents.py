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

    @staticmethod
    def prepare_study_name(model_object: Concept) -> List[str]:
        """Return a list of related studies"""
        studies = Study.objects.filter(topics__concepts__id=model_object.id).distinct()
        return [study.title() for study in studies]

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}concepts"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Concept

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

    @staticmethod
    def prepare_study_name(model_object: Topic) -> str:
        """Return the related study"""
        return model_object.study.title()

    @staticmethod
    def _get_study(model_object: Topic) -> Study:
        return model_object.study

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}topics"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Topic

    def get_queryset(self) -> Any:
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

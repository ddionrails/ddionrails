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

from typing import List

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.studies.models import Study

from .models import Concept, Topic


@registry.register_document
class ConceptDocument(Document):
    """ Search document for concepts.Concept """

    # doc_type was removed in Elasticsearch 7
    type = fields.KeywordField()

    @staticmethod
    def prepare_type(_: Concept) -> str:
        """Function seems to be necessary for elasticsearch to work."""
        return "concept"

    # attributes
    name = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")

    # facets
    study = fields.ListField(fields.KeywordField())

    @staticmethod
    def prepare_study(concept: Concept) -> List[str]:
        """ Return a list of related studies """
        studies_by_topic = Study.objects.filter(
            topics__concepts__id=concept.id
        ).distinct()
        studies_by_variable = Study.objects.filter(
            datasets__variables__concept_id=concept.id
        ).distinct()
        studies_by_question = Study.objects.filter(
            instruments__questions__concepts_questions__concept_id=concept.id
        ).distinct()
        studies = studies_by_topic.union(studies_by_variable).union(studies_by_question)
        return [study.title() for study in studies]

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}concepts"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Concept

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related objects.
        """
        return super().get_queryset().prefetch_related("variables", "concepts_questions")


@registry.register_document
class TopicDocument(Document):
    """ Search document for concepts.Topic """

    # doc_type was removed in Elasticsearch 7
    type = fields.KeywordField()

    @staticmethod
    def prepare_type(_: Topic) -> str:
        """Function seems to be necessary for elasticsearch to work."""
        return "topic"

    # attributes
    name = fields.TextField()
    label = fields.TextField(analyzer="english")
    label_de = fields.TextField(analyzer="german")
    description = fields.TextField(analyzer="english")
    description_de = fields.TextField(analyzer="german")

    # facets
    study = fields.KeywordField()

    @staticmethod
    def prepare_study(topic: Topic) -> str:
        """ Return the related study """
        return topic.study.title()

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}topics"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Topic

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

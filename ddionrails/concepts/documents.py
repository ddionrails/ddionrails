# -*- coding: utf-8 -*-

""" Search document definitions for ddionrails.concepts app """

from django.conf import settings
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.documents import Document
from django_elasticsearch_dsl.registries import registry

from ddionrails.studies.models import Study

from .models import Concept, Topic


@registry.register_document
class ConceptDocument(Document):
    """ Search document for concepts.Concept """

    # facets
    study = fields.ListField(fields.KeywordField())

    @staticmethod
    def prepare_study(concept: Concept):
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
        studies = (
            studies_by_topic.union(studies_by_variable)
            .union(studies_by_question)
            .distinct()
        )
        return [study.title() for study in studies]

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        # Set the "_type" attribute in Elasticsearch
        doc_type = "concept"

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}concepts"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Concept
        fields = ("name", "label", "label_de", "description", "description_de")


@registry.register_document
class TopicDocument(Document):
    """ Search document for concepts.Topic """

    # facets
    study = fields.TextField(fields={"raw": fields.KeywordField()})

    @staticmethod
    def prepare_study(topic: Topic) -> str:
        """ Return the related study """
        return topic.study.title()

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        # Set the "_type" attribute in Elasticsearch
        doc_type = "topic"

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}topics"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Topic
        fields = ("name", "label", "label_de", "description", "description_de")

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

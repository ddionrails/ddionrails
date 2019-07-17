# -*- coding: utf-8 -*-

""" Search document definitions for ddionrails.publications app """

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Publication


@registry.register_document
class PublicationDocument(Document):
    """ Search document for publications.Publication """

    # facets
    sub_type = fields.KeywordField()
    study = fields.KeywordField()
    year = fields.KeywordField()

    # prepare_FIELD will be executed while indexing FIELD
    @staticmethod
    def prepare_study(publication: Publication) -> str:
        """ Return the related study """
        return publication.study.title()

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        # Set the "_type" attribute in Elasticsearch
        doc_type = "publication"

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        # Name of the Elasticsearch index
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}publications"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Publication  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = ("abstract", "author", "cite", "doi", "name", "title", "url")

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

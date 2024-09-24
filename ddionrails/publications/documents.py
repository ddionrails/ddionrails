# -*- coding: utf-8 -*-

""" Document class for indexing Publication model in Elasticsearch


Authors:
    * 2019 Heinz-Alexander Fütterer (DIW Berlin)

License:
    | **AGPL-3.0 GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) 3.0**.
    | See LICENSE at the GitHub
      `repository <https://github.com/ddionrails/ddionrails/blob/master/LICENSE.md>`_
    | or at
      `<https://www.gnu.org/licenses/agpl-3.0.txt>`_.
"""

from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from ddionrails.base.generic_documents import GenericDocument
from ddionrails.studies.models import Study

from .models import Publication


@registry.register_document
class PublicationDocument(GenericDocument):
    """Search document for publications.Publication"""

    # facets
    sub_type = fields.KeywordField()
    year = fields.KeywordField()

    @staticmethod
    def prepare_description(publication: Publication) -> str:
        """Store abstract in general description field."""
        return publication.abstract

    @staticmethod
    def _get_study(model_object: Publication) -> Study:
        """Return the related study"""
        return model_object.study

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        # Name of the Elasticsearch index
        name = f"{settings.ELASTICSEARCH_DSL_INDEX_PREFIX}publications"

    class Django:  # pylint: disable=missing-docstring,too-few-public-methods
        model = Publication  # The model associated with this Document
        queryset_pagination = 5000  # TODO: Find out if this is the best fix

        # The fields of the model you want to be indexed in Elasticsearch
        fields = ("abstract", "author", "cite", "doi", "title", "url")

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset that should be indexed by this doc type,
        with select related study.
        """
        return super().get_queryset().select_related("study")

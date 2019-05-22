# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.studies app """

import os

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel

from ddionrails.base.mixins import ModelMixin as DorMixin
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin


class TopicList(ElasticMixin):

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "topiclist"

    def __init__(self, study):
        self.id = study.id


class Study(ElasticMixin, DorMixin, TimeStampedModel):
    """
    Stores a single study,
    related to :model:`data.Dataset`, :model:`instruments.Instrument`,
    :model:`concepts.Period` and :model:`workspace.Basket`.
    """

    # attributes
    name = models.CharField(
        max_length=255, unique=True, db_index=True, help_text="Name of the study"
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the study (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Label (German)",
        help_text="Label of the study (German)",
    )
    description = models.TextField(
        blank=True, help_text="Description of the study (Markdown)"
    )
    repo = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reference to the Git repository without definition of the protocol (e.g. https)",
    )
    current_commit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Commit hash of the last metadata import. This field is automatically filled by DDI on Rails",
    )
    config = JSONField(
        default=dict, blank=True, null=True, help_text="Configuration of the study (JSON)"
    )

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "study"

    class Meta:
        """ Django's metadata options """

        verbose_name_plural = "Studies"

    class DOR:
        """ ddionrails' metadata options """

        io_fields = ["name", "label", "description"]
        id_fields = ["name"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "name" field """
        return reverse("study_detail", kwargs={"study_name": self.name})

    def import_path(self):
        path = os.path.join(
            settings.IMPORT_REPO_PATH, self.name, settings.IMPORT_SUB_DIRECTORY
        )
        return path

    def repo_url(self) -> str:
        if settings.GIT_PROTOCOL == "https":
            return f"https://{self.repo}.git"
        elif settings.GIT_PROTOCOL == "ssh":
            return f"git@{self.repo}.git"
        else:
            raise Exception("Specify a protocol for Git in your settings.")

    def set_topiclist(self, body):
        t = TopicList(self)
        t.set_elastic(body)

    def get_topic_languages(self):
        return self.get_source().get("topic_languages", [])

    def has_topics(self) -> bool:
        return len(self.get_topic_languages()) > 0

    def get_topiclist(self, language="en"):
        t = TopicList(self)
        all_lists = t.get_source().get("topiclist")
        for topiclist in all_lists:
            if topiclist.get("language", "") == language:
                return topiclist.get("topics")


def context(request):
    return dict(all_studies=Study.objects.all().only("name", "label", "description"))

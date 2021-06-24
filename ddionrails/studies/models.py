# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.studies app """

import uuid
from typing import List, Optional

from django.apps import apps
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from django.urls import reverse
from model_utils.models import TimeStampedModel

from ddionrails.base.mixins import ImportPathMixin, ModelMixin
from ddionrails.imports.helpers import hash_with_base_uuid


class TopicList(models.Model):
    """
    Stores a single topiclist, related to :model:`studies.Study`.
    """

    id = models.AutoField(primary_key=True)

    ##############
    # attributes #
    ##############
    topiclist = JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="Topics of the related study (JSON)",
    )

    #############
    # relations #
    #############
    study = models.OneToOneField(
        "Study",
        blank=True,
        null=True,
        related_name="topiclist",
        on_delete=models.CASCADE,
        help_text="OneToOneField to studies.Study",
    )


class Study(ImportPathMixin, ModelMixin, TimeStampedModel):
    """
    Stores a single study,
    related to :model:`data.Dataset`, :model:`instruments.Instrument`,
    :model:`concepts.Period` and :model:`workspace.Basket`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the study",
    )
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
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the study (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the study (Markdown, German)",
    )
    doi = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="DOI",
        help_text="DOI of the study (DOI only, not the URL to the DOI)",
    )
    repo = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Reference to the Git repository "
            "without definition of the protocol (e.g. https)"
        ),
    )
    current_commit = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Commit hash of the last metadata import. "
            "This field is automatically filled by DDI on Rails"
        ),
    )
    config = JSONField(
        default=dict, blank=True, null=True, help_text="Configuration of the study (JSON)"
    )
    topic_languages = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        help_text="Topic languages of the study (Array)",
    )

    #############
    # relations #
    #############

    topiclist = TopicList

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        verbose_name_plural = "Studies"

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        io_fields = ["name", "label", "description"]
        id_fields = ["name"]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_base_uuid(self.name, cache=False)  # pylint: disable=C0103

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "name" field """
        return reverse("study_detail", kwargs={"study_name": self.name})

    def repo_url(self) -> str:
        """ Assembles the Git remote url. """
        if settings.GIT_PROTOCOL == "https":
            return f"https://{self.repo}.git"
        if settings.GIT_PROTOCOL == "ssh":
            return f"git@{self.repo}.git"

        raise Exception("Specify a protocol for Git in your settings.")

    def set_topiclist(self, body: List) -> None:
        """ Changes the topiclists content """
        _topiclist, _ = TopicList.objects.get_or_create(study=self)
        _topiclist.topiclist = body
        _topiclist.save()

    def has_topics(self) -> bool:
        """ Returns True if the study has topics. """
        topic_model = apps.get_model("concepts", "Topic")
        return bool(topic_model.objects.filter(study=self)[:1])

    def get_topiclist(self, language: str = "en") -> Optional[List]:
        """ Returns the list of topics for a given language or None """
        try:
            for topiclist in self.topiclist.topiclist:
                if topiclist.get("language", "") == language:
                    return topiclist.get("topics")
        except TopicList.DoesNotExist:
            return None
        else:
            return None

# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: Instrument """

import uuid

from django.db import models
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import AnalysisUnit, Period
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.studies.models import Study


class Instrument(ModelMixin, models.Model):
    """
    Stores a single instrument,
    related to :model:`studies.Study`,
    :model:`concepts.Period` and :model:`concepts.AnalysisUnit`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the instrument. Dependent on the associated study.",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        db_index=True,
        help_text="Name of the instrument (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the instrument (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the instrument (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the instrument (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the instrument (Markdown, German)",
    )
    mode = models.TextField(
        blank=True,
        default="",
        verbose_name="Mode of inquiry.",
        help_text="The procedure, technique, or mode of inquiry used to attain the data.",
    )
    type = models.JSONField(
        blank=True,
        default={},
        verbose_name="Instrument type",
        help_text="Categorization for instruments",
    )
    has_questions = models.BooleanField(
        blank=False,
        default=False,
        help_text="Flag if instrument has Questions associated with it.",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )
    period = models.ForeignKey(
        Period,
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.Period",
    )
    analysis_unit = models.ForeignKey(
        AnalysisUnit,
        blank=True,
        null=True,
        related_name="instruments",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.AnalysisUnit",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """ "Set id and call parents save()."""
        self.id = hash_with_namespace_uuid(  # pylint: disable=invalid-name
            self.study_id, self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")
        ordering = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "period", "analysis_unit"]

    def get_absolute_url(self) -> str:
        """Returns a canonical URL for the model using the "study" and "name" fields"""
        return reverse(
            "instruments:instrument_detail",
            kwargs={"study": self.study, "instrument_name": self.name},
        )

    def get_direct_url(self) -> str:
        """Returns a canonical URL for the model using the "study" and "name" fields"""
        return reverse("instrument_redirect", kwargs={"id": self.id})

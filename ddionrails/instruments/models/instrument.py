# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: Instrument """

from django.db import models
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import AnalysisUnit, Period
from ddionrails.studies.models import Study


class Instrument(ModelMixin, models.Model):
    """
    Stores a single instrument,
    related to :model:`studies.Study`, :model:`concepts.Period` and :model:`concepts.AnalysisUnit`.
    """

    # attributes
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
        verbose_name="Description (Markdown)",
        help_text="Description of the topic (Markdown)",
    )

    # relations
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

    class Meta:
        """ Django's metadata options """

        unique_together = ("study", "name")
        ordering = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "period", "analysis_unit"]

    def __str__(self) -> str:
        """ Returns a string representation using the "study" and "name" fields """
        return f"{self.study}/inst/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse(
            "inst:instrument_detail",
            kwargs={"study_name": self.study.name, "instrument_name": self.name},
        )

    @staticmethod
    def layout_class() -> str:
        return "instrument"

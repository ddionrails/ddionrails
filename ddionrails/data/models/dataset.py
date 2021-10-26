# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Dataset """

import uuid

from django.db import models
from django.urls import reverse

from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.studies.models import Study


class Dataset(ModelMixin, models.Model):
    """
    Stores a single dataset,
    related to :model:`studies.Study`, :model:`concepts.ConceptualDataset`,
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
        help_text="UUID of the dataset. Dependent on the associated study.",
    )

    name = models.CharField(
        max_length=255, db_index=True, help_text="Name of the dataset"
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the dataset (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Label (German)",
        help_text="Label of the dataset (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the dataset (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the dataset (Markdown, German)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        blank=True,
        null=True,
        related_name="datasets",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )
    conceptual_dataset = models.ForeignKey(
        ConceptualDataset,
        blank=True,
        null=True,
        related_name="datasets",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.ConceptualDataset",
    )
    period = models.ForeignKey(
        Period,
        blank=True,
        null=True,
        related_name="datasets",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.Period",
    )
    analysis_unit = models.ForeignKey(
        AnalysisUnit,
        blank=True,
        null=True,
        related_name="datasets",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.AnalysisUnit",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(
            self.study_id, self.name, cache=False
        )  # pylint: disable=C0103
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    class DOR(ModelMixin.DOR):  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["study", "name"]

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse(
            "data:dataset_detail",
            kwargs={"study_name": self.study.name, "dataset_name": self.name},
        )

    def get_direct_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse("dataset_redirect", kwargs={"id": self.id})

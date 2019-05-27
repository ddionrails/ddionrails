# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Dataset """

from django.db import models
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin as DorMixin
from ddionrails.concepts.models import AnalysisUnit, ConceptualDataset, Period
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin
from ddionrails.studies.models import Study


class Dataset(ElasticMixin, DorMixin, models.Model):
    """
    Stores a single dataset,
    related to :model:`studies.Study`, :model:`concepts.ConceptualDataset`,
    :model:`concepts.Period` and :model:`concepts.AnalysisUnit`.
    """

    # attributes
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        db_index=True,
        help_text="Name of the dataset (Lowercase)",
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
        help_text="Label of the dataset (German",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown)",
        help_text="Description of the dataset (Markdown)",
    )
    boost = models.FloatField(
        blank=True,
        null=True,
        help_text="Boost factor to be used in search (Elasticsearch)",
    )

    # relations
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

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "dataset"

    class Meta:
        """ Django's metadata options """

        unique_together = ("study", "name")

    class DOR(DorMixin.DOR):
        """ ddionrails' metadata options """

        id_fields = ["study", "name"]

    def __str__(self) -> str:
        """ Returns a string representation using the "study" and "name" fields """
        return f"{self.study}/data/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse(
            "data:dataset",
            kwargs={"study_name": self.study.name, "dataset_name": self.name},
        )

# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Transformation """

from __future__ import annotations

from django.db import models

from .variable import Variable


class Transformation(models.Model):
    """
    Stores a single transformation, related to :model:`data.Variable`.
    """

    #############
    # relations #
    #############
    origin = models.ForeignKey(
        Variable,
        related_name="target_variables",
        on_delete=models.CASCADE,
        verbose_name="Origin (data.Variable)",
        help_text="Foreign key to data.Variable",
    )
    target = models.ForeignKey(
        Variable,
        related_name="origin_variables",
        on_delete=models.CASCADE,
        verbose_name="Target (data.Variable)",
        help_text="Foreign key to data.Variable",
    )

    class Meta:
        """ Django's metadata options """

        unique_together = ("origin", "target")

    @classmethod
    def goc_by_name(
        cls,
        origin_study: str,
        origin_dataset: str,
        origin_variable: str,
        target_study: str,
        target_dataset: str,
        target_variable: str,
    ) -> Transformation:
        """ Create a tranformation by:
                origin: study_name, dataset_name, variable_name
                and
                target: study_name, dataset_name, variable_name
        """
        origin = (
            Variable.objects.filter(dataset__study__name=origin_study)
            .filter(dataset__name=origin_dataset)
            .get(name=origin_variable)
        )
        target = (
            Variable.objects.filter(dataset__study__name=target_study)
            .filter(dataset__name=target_dataset)
            .get(name=target_variable)
        )
        return cls.objects.get_or_create(origin=origin, target=target)

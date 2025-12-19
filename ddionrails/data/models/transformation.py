# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Transformation """

from __future__ import annotations

from django.db import models
from django.utils.functional import empty

from .variable import Variable


class Transformation(models.Model):
    """
    Stores a single transformation, related to :model:`data.Variable`.
    """

    #############
    # relations #
    #############

    id = models.AutoField(primary_key=True)

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

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("origin", "target")

class Sibling(models.Model):

    id = models.AutoField(primary_key=True)

    sibling_a = models.ForeignKey(
            Variable,
            on_delete=models.CASCADE,
            )

    sibling_b = models.ForeignKey(
            Variable,
            related_name="siblings",
            on_delete=models.CASCADE,
            )

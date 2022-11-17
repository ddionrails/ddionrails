# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: ItemVariable """

from django.db import models

from ddionrails.data.models.variable import Variable

from .question_item import QuestionItem


class ItemVariable(models.Model):
    """
    Stores a single question variable,
    related to :model:`instruments.Question` and :model:`data.Variable`.

    Linking items in an instrument with related variables.
    """

    id = models.AutoField(primary_key=True)

    #############
    # relations #
    #############
    item = models.ForeignKey(
        QuestionItem,
        related_name="variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to instruments.Question",
    )
    variable = models.ForeignKey(
        Variable,
        related_name="items",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("item", "variable")

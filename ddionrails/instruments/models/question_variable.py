# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: QuestionVariable """

from django.db import models

from ddionrails.data.models import Variable

from .question import Question


class QuestionVariable(models.Model):
    """
    Stores a single question variable,
    related to :model:`instruments.Question` and :model:`data.Variable`.

    Linking items in an instrument with related variables.
    """

    # relations
    question = models.ForeignKey(
        Question,
        related_name="questions_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to instruments.Question",
    )
    variable = models.ForeignKey(
        Variable,
        related_name="questions_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("question", "variable")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["question", "variable"]
        io_fields = ["question", "variable"]

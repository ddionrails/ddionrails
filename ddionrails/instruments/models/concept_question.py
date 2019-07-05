# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: ConceptQuestion """

from django.db import models

from ddionrails.concepts.models import Concept

from .question import Question


class ConceptQuestion(models.Model):
    """
    Stores a single concept question,
    related to :model:`instruments.Question` and :model:`concepts.Concept`.

    Linking items in an instrument with related variables.
    """

    #############
    # relations #
    #############
    question = models.ForeignKey(
        Question,
        related_name="concepts_questions",
        on_delete=models.CASCADE,
        help_text="Foreign key to instruments.Question",
    )
    concept = models.ForeignKey(
        Concept,
        related_name="concepts_questions",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.Concept",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("question", "concept")

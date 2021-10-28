# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.instruments app: Question """

from __future__ import annotations

import copy
import textwrap
import uuid
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Union

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import JSONField as JSONBField
from django.db.models import QuerySet
from django.urls import reverse

from config.helpers import render_markdown
from ddionrails.base.helpers.ddionrails_typing import QuestionItemType
from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import Concept, Period
from ddionrails.imports.helpers import hash_with_namespace_uuid

from .instrument import Instrument


class Question(ModelMixin, models.Model):
    """
    Stores a single question, related to :model:`instruments.Instrument`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=invalid-name
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the question. Dependent on the associated instrument.",
    )
    name = models.CharField(
        max_length=255, db_index=True, help_text="Name of the question"
    )
    label = models.TextField(
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the question (English)",
    )
    label_de = models.TextField(
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the question (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the question (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the question (Markdown, German)",
    )
    instruction = models.TextField(
        blank=True,
        default="",
        verbose_name="Instruction",
        help_text="Optional question instruction.",
    )
    instruction_de = models.TextField(
        blank=True,
        default="",
        verbose_name="Instruction German",
        help_text="Optional german question instruction.",
    )
    sort_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sort ID",
        help_text="Sort order of questions within one instrument",
    )
    items = JSONBField(
        default=list, null=True, blank=True, help_text="Items are elements in a question"
    )
    question_items: models.manager.Manager[Any]

    #############
    # relations #
    #############
    instrument = models.ForeignKey(
        Instrument,
        blank=True,
        null=False,
        related_name="questions",
        on_delete=models.CASCADE,
    )

    period = models.ForeignKey(
        Period, blank=True, null=True, related_name="period", on_delete=models.SET_NULL
    )

    def generate_id(self, cache=False):
        """Generate UUID used in the objects save method."""
        return hash_with_namespace_uuid(self.instrument_id, self.name, cache=cache)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        if not self.period:
            self.period = self.instrument.period

        self.id = self.generate_id()  # pylint: disable=invalid-name
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("instrument", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["instrument", "name"]
        io_fields = ["name", "label", "description", "instrument"]

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model

        Uses the "study", "instrument" and "name" fields
        """
        return reverse(
            "inst:question_detail",
            kwargs={
                "study_name": self.instrument.study.name,
                "instrument_name": self.instrument.name,
                "question_name": self.name,
            },
        )

    def get_direct_url(self) -> str:
        """ Returns a canonical URL for the model

        Uses the "study", "instrument" and "name" fields
        """
        return reverse("question_redirect", kwargs={"id": self.id})

    @staticmethod
    def layout_class() -> str:
        """ Returns the layout class (used in templates) """
        return "question"

    def previous_question(self) -> Optional[Question]:
        """ Returns the previous question object or None
            i.e. the question object with the preceding sort_id
        """
        try:
            return self.instrument.questions.get(sort_id=self.sort_id - 1).name
        except ObjectDoesNotExist:
            return None

    def next_question(self) -> Optional[Question]:
        """ Returns the next question object or None
            i.e. the question object with the following sort_id
        """
        try:
            return self.instrument.questions.get(sort_id=self.sort_id + 1).name
        except ObjectDoesNotExist:
            return None

    def get_related_questions(self) -> OrderedDict[str, Question]:
        """ Get all related questions categorized by their period """
        study = self.instrument.study
        concept_list = self.get_concepts()
        questions = (
            Question.objects.filter(
                concepts_questions__concept_id__in=concept_list,
                instrument__study_id=study,
            )
            .distinct()
            .prefetch_related("instrument", "instrument__period")
        )
        result: OrderedDict = OrderedDict()
        result = OrderedDict()
        result["no period"] = []
        for period in study.periods.order_by("name"):
            result[period.name] = []
        for question in questions:
            result[question.instrument.period.name].append(question)
        return result

    def get_concepts(self) -> QuerySet:
        """ Retrieve the related Concepts of this Question

            A question and concept are related if
            their relation is defined in ConceptQuestion.
        """
        return Concept.objects.filter(concepts_questions__question_id=self.pk).distinct()

    def translation_languages(self) -> List[str]:
        """ Returns a list of translation languages, e.g. ["de"] """
        keys = list(self.items[0].keys())
        keys_first_item = copy.deepcopy(keys)
        return [key.replace("text_", "") for key in keys_first_item if "text_" in key]

    @staticmethod
    def overwrite_item_values_by_language(item: QuestionItemType, language: str) -> None:
        """Switch values with their counterparts in the specified language."""
        item["text"] = item.get(f"text_{language}", item.get("text", ""))
        item["instruction"] = item.get(
            f"instruction_{language}", item.get("instruction", "")
        )
        for answer in item.get("answers", []):
            answer["label"] = answer.get(f"label_{language}", answer.get("label", ""))

    def to_topic_dict(self, language: str = "en") -> Dict:
        """ Returns a topic dictionary representation of the Question object """
        if language == "de":
            title = self.label_de if self.label_de != "" else self.title()
        else:
            title = self.title()
        try:
            concept_name = self.questions_variables.first().variable.concept.name
        # afuetterer: there might be no concept?
        except AttributeError:
            concept_name = ""
        return dict(
            title=title,
            key="question_%s" % self.id,
            name=self.name,
            type="question",
            concept_key="concept_%s" % concept_name,
        )

    def html_description(self) -> str:
        """ Return question description as HTML. """
        return render_markdown(self.description)

    def comparison_string(
        self, to_string: bool = False, wrap: int = 50
    ) -> Union[str, List]:
        """
        pylint: disable=fixme
        TODO: instruments.models.question.comparison_string needs docstring
        """
        comparison_string_array = ["Question: %s" % self.title()]
        for item in self.items:
            comparison_string_array += [
                "",
                "Item: %s (scale: %s)" % (item.get("item"), item.get("scale")),
                item.get("text", ""),
            ]
            comparison_string_array += [
                "%s: %s" % (a["value"], a["label"]) for a in item.get("answers", [])
            ]
        if wrap:
            cs_temp = [textwrap.wrap(line, wrap) for line in comparison_string_array]
            comparison_string_array = []
            for line_list in cs_temp:
                if line_list == []:
                    comparison_string_array.append("")
                else:
                    comparison_string_array += line_list
        if to_string:
            return "\n".join(comparison_string_array)
        return comparison_string_array

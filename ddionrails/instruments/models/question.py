# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.instruments app: Question """
from __future__ import annotations

import copy
import textwrap
from collections import OrderedDict
from typing import List, Optional

from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin as DorMixin
from ddionrails.concepts.models import Concept
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin
from ddionrails.studies.models import Study

from .instrument import Instrument


class Question(ElasticMixin, DorMixin, models.Model):
    """
    Stores a single question, related to :model:`instruments.Tnstrument`.
    """

    # attributes
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        db_index=True,
        help_text="Name of the question (Lowercase)",
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
        verbose_name="Description (Markdown)",
        help_text="Description of the topic (Markdown)",
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

    # relations
    instrument = models.ForeignKey(
        Instrument,
        blank=True,
        null=True,
        related_name="questions",
        on_delete=models.CASCADE,
    )

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "question"

    class Meta:
        """ Django's metadata options """

        unique_together = ("instrument", "name")

    class DOR:
        """ ddionrails' metadata options """

        id_fields = ["instrument", "name"]
        io_fields = ["name", "label", "description", "instrument"]

    def __str__(self) -> str:
        """ Returns a string representation using the "instrument" and "name" fields """
        return f"{self.instrument}/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study", "instrument" and "name" fields"""
        return reverse(
            "inst:question_detail",
            kwargs={
                "study_name": self.instrument.study.name,
                "instrument_name": self.instrument.name,
                "question_name": self.name,
            },
        )

    def layout_class(self) -> str:
        return "question"

    def previous_question(self) -> Optional[Question]:
        """ Returns the previous question object or None
            i.e. the question object with the preceding sort_id
        """
        try:
            return self.instrument.questions.get(sort_id=self.sort_id - 1)
        except ObjectDoesNotExist:
            return None

    def next_question(self) -> Optional[Question]:
        """ Returns the next question object or None
            i.e. the question object with the following sort_id
        """
        try:
            return self.instrument.questions.get(sort_id=self.sort_id + 1)
        except ObjectDoesNotExist:
            return None

    def get_period(self, id=False, default=None):
        try:
            p = self.instrument.period
            if id == True:
                return p.id
            elif id == "name":
                return p.name
            else:
                return p
        except:
            return default

    def get_related_question_set(self, all_studies=False, by_study_and_period=False):
        concept_list = self.get_concepts()
        if all_studies:
            study_list = Study.objects.all()
        else:
            study_list = [self.instrument.study]
        direct_questions = Question.objects.filter(
            concepts_questions__concept_id__in=concept_list,
            instrument__study_id__in=study_list,
        )
        indirect_questions = Question.objects.filter(
            questions_variables__variable__concept__in=concept_list,
            instrument__study_id__in=study_list,
        )
        combined_set = direct_questions | indirect_questions
        combined_set = combined_set.distinct()
        if by_study_and_period:
            result = OrderedDict()
            for study in study_list:
                result[study.name] = OrderedDict()
                result[study.name]["no period"] = list()
                for period in study.periods.order_by("name"):
                    result[study.name][period.name] = list()
            for question in combined_set:
                result[question.instrument.study.name][
                    question.get_period(id="name", default="no period")
                ].append(question)
            return result
        else:
            return combined_set

    def get_concepts(self) -> QuerySet:
        """ Retrieve the related Concepts of this Question

            A question and concept are related if
            their relation is defined in ConceptQuestion.
        """
        return Concept.objects.filter(concepts_questions__question_id=self.pk).distinct()

    def concept_list(self):
        """DEPRECATED NAME"""
        return self.get_concepts()

    def get_cs_name(self):
        x = self.get_source().get("question", "")
        if x != "":
            return x
        else:
            return self.name

    def title(self):
        if self.label != None and self.label != "":
            return self.label
        try:
            return self.items.first().title()
        except:
            return self.name

    def title_de(self):
        if self.label_de != None and self.label_de != "":
            return self.label
        try:
            return self.items.first().title_de()
        except:
            return self.name

    def translation_languages(self) -> List[str]:
        """ Returns a list of translation languages, e.g. ["de"] """
        keys = list(self.items[0].keys())
        keys_first_item = copy.deepcopy(keys)
        return [x.replace("text_", "") for x in keys_first_item if ("text_" in x)]

    def translate_item(self, item, language):
        item["text"] = item.get("text_%s" % language, item.get("text", ""))
        item["instruction"] = item.get(
            "instruction_%s" % language, item.get("instruction", "")
        )
        for answer in item.get("answers", []):
            answer["label"] = answer.get("label_%s" % language, answer.get("label", ""))

    def translations(self):
        results = {}
        try:
            for language in self.translation_languages():
                results[language] = self.item_array(language=language)
        except:
            pass
        return results

    def item_array(self, language=None):
        items = copy.deepcopy(self.items)
        items = items.values() if items.__class__ == dict else items
        for item in items:
            if language:
                self.translate_item(item, language)
            if "item" not in item:
                item["item"] = "root"
            if "sn" not in item:
                item["sn"] = 0
        items = sorted(items, key=lambda x: int(x["sn"]))
        before = None
        for i in range(len(items)):
            try:
                current = items[i]["answer_list"]
            except:
                current = None
            try:
                after = items[i + 1]["answer_list"]
            except:
                after = None
            if current and current == before:
                if current == after:
                    items[i]["layout"] = "matrix_element"
                else:
                    items[i]["layout"] = "matrix_footer"
            elif current and current == after:
                items[i]["layout"] = "matrix_header"
            else:
                items[i]["layout"] = "individual"
            before = current
        return items

    def to_topic_dict(self, language="en"):
        if language == "de":
            title = self.label_de if self.label_de != "" else self.title()
        else:
            title = self.title()
        try:
            concept_name = self.questions_variables.first().variable.concept.name
        except:
            concept_name = ""
        return dict(
            title=title,
            key="question_%s" % self.id,
            name=self.name,
            type="question",
            concept_key="concept_%s" % concept_name,
        )

    def comparison_string(self, to_string=False, wrap=50):
        cs = ["Question: %s" % self.title()]
        for item in self.items:
            cs += [
                "",
                "Item: %s (scale: %s)" % (item.get("item"), item.get("scale")),
                item.get("text", ""),
            ]
            cs += ["%s: %s" % (a["value"], a["label"]) for a in item.get("answers", [])]
        if wrap:
            cs_temp = [textwrap.wrap(line, wrap) for line in cs]
            cs = []
            for line_list in cs_temp:
                if line_list == []:
                    cs.append("")
                else:
                    cs += line_list
        if to_string:
            return "\n".join(cs)
        else:
            return cs

# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Variable """

from __future__ import annotations

from collections import OrderedDict
from typing import List, Dict

from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from filer.fields.image import FilerImageField

from config.helpers import render_markdown
from ddionrails.base.mixins import ModelMixin as DorMixin
from ddionrails.concepts.models import Concept, Period
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin
from ddionrails.studies.models import Study

from .dataset import Dataset


class Variable(ElasticMixin, DorMixin, models.Model):
    """
    Stores a single variable,
    related to :model:`data.Dataset`, :model:`concepts.Concept` and :model:`concepts.Period`.
    """

    # attributes
    name = models.CharField(
        max_length=255, db_index=True, help_text="Name of the variable"
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the variable (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Label (German)",
        help_text="Label of the variable (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown)",
        help_text="Description of the variable (Markdown)",
    )
    description_long = models.TextField(
        blank=True,
        verbose_name="Extended description (Markdown)",
        help_text="Extended description of the variable (Markdown)",
    )
    sort_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Sort ID",
        help_text="Sort order of variables within one dataset",
    )
    image_url = models.TextField(
        blank=True, verbose_name="Image URL", help_text="URL to a related image"
    )
    statistics = JSONBField(
        default=dict, null=True, blank=True, help_text="Statistics of the variable(JSON)"
    )
    scale = models.CharField(
        max_length=255, null=True, blank=True, help_text="Scale of the variable"
    )
    categories = JSONBField(
        default=list, null=True, blank=True, help_text="Categories of the variable(JSON)"
    )

    # relations
    dataset = models.ForeignKey(
        Dataset,
        blank=True,
        null=True,
        related_name="variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Dataset",
    )
    concept = models.ForeignKey(
        Concept,
        blank=True,
        null=True,
        related_name="variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.Concept",
    )
    period = models.ForeignKey(
        Period,
        blank=True,
        null=True,
        related_name="variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to concepts.Period",
    )
    image = FilerImageField(null=True, blank=True, on_delete=models.CASCADE)

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "variable"

    class Meta:
        """ Django's metadata options """

        unique_together = ("name", "dataset")

    class DOR(DorMixin.DOR):
        """ ddionrails' metadata options """

        id_fields = ["name", "dataset"]

    def __str__(self) -> str:
        """ Returns a string representation using the "dataset" and "name" fields """
        return f"{self.dataset}/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "dataset" and "name" fields """
        return reverse(
            "data:variable",
            kwargs={
                "study_name": self.dataset.study.name,
                "dataset_name": self.dataset.name,
                "variable_name": self.name,
            },
        )

    @classmethod
    def get(cls, x: dict) -> Variable:
        study = get_object_or_404(Study, name=x["study_name"])
        dataset = get_object_or_404(Dataset, name=x["dataset_name"], study=study)
        variable = get_object_or_404(cls, name=x["name"], dataset=dataset)
        return variable

    @classmethod
    def get_by_concept_id(cls, concept_id):
        return cls.objects.filter(concept_id=concept_id)

    def html_description_long(self):
        try:
            html = render_markdown(self.description_long)
        except:
            html = ""
        return html

    def get_categories(self) -> List:
        if self.categories:
            categories = []
            for index in range(len(self.categories["values"])):
                categories.append(
                    dict(
                        value=self.categories["values"][index],
                        label=self.categories["labels"][index],
                        label_de=self.categories["labels_de"][index],
                        frequency=self.categories["frequencies"][index],
                        valid=(not self.categories["missings"][index]),
                    )
                )
            return categories
        else:
            return []

    def get_study(self, default=None, id=False):
        try:
            if id:
                return self.dataset.study.id
            else:
                return self.dataset.study
        except:
            return default

    def get_concept(self, default=None, id=False):
        try:
            if id:
                return self.concept.id
            else:
                return self.concept
        except:
            return default

    def get_period(self, default=None, id=False):
        try:
            p1 = self.dataset.period
            p2 = self.period
            p = p2 if p2 else p1
            if id == True:
                return p.id
            elif id == "name":
                return p.name
            else:
                return p
        except:
            return default

    def get_related_variables(self):
        if self.concept:
            variables = (
                self.__class__.objects.select_related(
                    "dataset", "dataset__study", "dataset__period"
                )
                .filter(concept_id=self.concept.id)
                .filter(dataset__study_id=self.dataset.study.id)
            )
        else:
            variables = []
        return variables

    def get_related_variables_by_period(self):
        results = dict()
        periods = Period.objects.filter(study_id=self.dataset.study.id).all()
        for period in periods:
            results[period.name] = list()
        if "none" not in results:
            results["none"] = list()
        for variable in self.get_related_variables():
            try:
                results[variable.dataset.period.name].append(variable)
            except:
                results["none"].append(variable)
        return OrderedDict(sorted(results.items()))

    def has_origin_variables(self):
        """
        TEMPORARY / DEPRECATED

        Find a better solution, when to show origin variables…
        """
        return self.origin_variables.count() > 0

    def get_targets_by_study_and_period(self, object_type="variable"):
        """
        Get objects that are based on an relationship through transformations
        in the direction to target (e.g., all wide variables, which a long
        variable is based on).

        :param object_type: type of return value
        :type object_type: "variable" or "question"
        :return: Nested dicts, study --> period --> list of variables/questions
        """
        target_variables = [x.target for x in self.target_variables.all()]
        studies = set(
            [target_variable.dataset.study for target_variable in target_variables]
        )
        result = OrderedDict()
        for study in studies:
            periods = Period.objects.filter(study_id=study.id).order_by("name").all()
            result[study.name] = OrderedDict()
            for period in periods:
                result[study.name][period.name] = list()
        for target_variable in target_variables:
            study_name = target_variable.dataset.study.name
            period_name = target_variable.get_period(id="name", default="no period")
            if object_type == "variable":
                result[study_name][period_name].append(target_variable)
            elif object_type == "question":
                result[study_name][
                    period_name
                ] += target_variable.questions_variables.all()
        return result

    def get_target_variables(self):
        return self.get_targets_by_study_and_period(object_type="variable")

    def get_origins_by_study_and_period(self, object_type="variable"):
        """
        Get objects that are based on an relationship through transformations
        in the direction to origin (e.g., all wide variables, which a long
        variable is based on).

        :param object_type: type of return value
        :type object_type: "variable" or "question"
        :return: Nested dicts, study --> period --> list of variables/questions
        """
        origin_variables = [x.origin for x in self.origin_variables.all()]
        studies = set(
            [origin_variable.dataset.study for origin_variable in origin_variables]
        )
        result = OrderedDict()
        for study in studies:
            periods = Period.objects.filter(study_id=study.id).order_by("name").all()
            result[study.name] = OrderedDict()
            for period in periods:
                result[study.name][period.name] = list()
        for origin_variable in origin_variables:
            study_name = origin_variable.dataset.study.name
            period_name = origin_variable.get_period(id="name", default="no period")
            if object_type == "variable":
                result[study_name][period_name].append(origin_variable)
            elif object_type == "question":
                result[study_name][
                    period_name
                ] += origin_variable.questions_variables.all()
        return result

    def get_origin_variables(self):
        return self.get_origins_by_study_and_period(object_type="variable")

    def get_origin_questions(self):
        return self.get_origins_by_study_and_period(object_type="question")

    def has_translations(self) -> bool:
        return len(self.translation_languages()) > 0

    def translation_languages(self) -> List[str]:
        if not hasattr(self, "languages"):
            self.languages = [
                label.replace("label_", "")
                for label in self.__dict__.keys()
                if ("label_" in label)
            ]
        return self.languages

    def translation_table(self) -> Dict:
        translation_table = dict(label=dict(en=self.label))
        for language in self.translation_languages():
            translation_table["label"][language] = getattr(self, f"label_{language}")

        for category in self.get_categories():
            translation_table[category["value"]] = dict(en=category["label"])
        for language in self.translation_languages():
            for category in self.get_categories():
                translation_table[category["value"]][language] = category.get(
                    f"label_{language}"
                )
        return translation_table

    def is_categorical(self) -> bool:
        return len(self.categories) > 0

    def title(self):
        return self.label if self.label != "" else self.name

    def title_de(self):
        if self.label_de != "" and self.label_de is not None:
            return self.label_de
        else:
            return self.title()

    def to_dict(self) -> Dict:
        return dict(
            name=self.name,
            label=self.label,
            label_de=self.label_de,
            concept_id=self.concept_id,
            scale=self.scale,
            uni=self.categories,
        )

    def to_topic_dict(self, language="en"):
        if language == "de":
            title = self.label_de if self.label_de != "" else self.title()
        else:
            title = self.title()
        return dict(
            key="variable_%s" % self.id,
            name=self.name,
            title=title,
            concept_key="concept_%s" % self.concept.name,
            type="variable",
        )

    @classmethod
    def index_prefetch(self, queryset):
        return (
            queryset.prefetch_related("dataset__study")
            .prefetch_related("dataset__period")
            .prefetch_related("period")
        )

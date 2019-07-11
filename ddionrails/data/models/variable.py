# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Variable """

from __future__ import annotations

import inspect
import uuid
from collections import OrderedDict
from typing import Dict, List, Union

from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from filer.fields.image import FilerImageField

from config.helpers import render_markdown
from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import Concept, Period
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.studies.models import Study

from .dataset import Dataset


class Variable(ModelMixin, models.Model):
    """
    Stores a single variable,
    related to :model:`data.Dataset`,
    :model:`concepts.Concept` and :model:`concepts.Period`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the variable. Dependent on the associated dataset.",
    )

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
        verbose_name="Description (Markdown, English)",
        help_text="Description of the variable (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the variable (Markdown, German)",
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
    languages = list()
    statistics = JSONBField(
        default=dict, null=True, blank=True, help_text="Statistics of the variable(JSON)"
    )
    scale = models.CharField(
        max_length=255, null=True, blank=True, help_text="Scale of the variable"
    )
    categories = JSONBField(
        default=list, null=True, blank=True, help_text="Categories of the variable(JSON)"
    )

    #############
    # relations #
    #############
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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(
            self.dataset_id, self.name, cache=False
        )  # pylint: disable=C0103
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("name", "dataset")

    class DOR(ModelMixin.DOR):  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["name", "dataset"]

    def __str__(self) -> str:
        """ Returns a string representation using the "dataset" and "name" fields """
        return f"{self.dataset}/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model.

        Uses the "dataset" and "name" fields
        """
        return reverse(
            "data:variable_detail",
            kwargs={
                "study_name": self.dataset.study.name,
                "dataset_name": self.dataset.name,
                "variable_name": self.name,
            },
        )

    @classmethod
    def get(cls, parameters: Dict) -> Variable:
        study = get_object_or_404(Study, name=parameters["study_name"])
        dataset = get_object_or_404(Dataset, name=parameters["dataset_name"], study=study)
        variable = get_object_or_404(cls, name=parameters["name"], dataset=dataset)
        return variable

    @classmethod
    def get_by_concept_id(cls, concept_id: int) -> QuerySet:
        """ Return a QuerySet of Variable objects by a given concept id """
        return cls.objects.filter(concept_id=concept_id)

    def html_description_long(self) -> str:
        """ Return a markdown rendered version of the "description_long" field """
        try:
            html = render_markdown(self.description_long)
        except:  # TODO: what could happen in render_markdown() ?
            html = ""
        return html

    def get_categories(self) -> List:
        """ Return a list of dictionaries based on the "categories" field """
        if self.categories:
            categories = []
            for index, _ in enumerate(self.categories["values"]):
                category = dict(
                    value=self.categories["values"][index],
                    label=self.categories["labels"][index],
                    frequency=self.categories["frequencies"][index],
                    valid=(not self.categories["missings"][index]),
                )
                if "labels_de" in self.categories:
                    category["label_de"] = self.categories["labels_de"][index]
                categories.append(category)
            return categories

        return []

    def get_study(self, study_id=False):
        """ Returns the related study_id | Study instance """
        if study_id:
            return self.dataset.study.id
        return self.dataset.study

    def get_concept(self, default=None, concept_id=False):
        """ Returns the related concept_id | Concept instance | a default """
        try:
            if concept_id:
                return self.concept.id
            return self.concept
        except AttributeError:
            return default

    def get_period(self, default=None, period_id=False):
        """ Returns the related period_id | period_name | Period instance | a default """
        try:
            period_1 = self.dataset.period
            period_2 = self.period
            period = period_2 if period_2 else period_1
            if period_id is True:
                return period.id
            if period_id == "name":
                return period.name
            return period
        except AttributeError:
            return default

    def get_related_variables(self) -> Union[List, QuerySet]:
        """ Returns the related variables by concept """
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

    def get_related_variables_by_period(self) -> OrderedDict:
        """ Returns the related variables by concept, ordered by period """
        results = dict()
        periods = Period.objects.filter(study_id=self.dataset.study.id).all()
        for period in periods:
            results[period.name] = list()
        if "none" not in results:
            results["none"] = list()
        for variable in self.get_related_variables():
            try:
                results[variable.dataset.period.name].append(variable)
            except AttributeError:
                results["none"].append(variable)
        return OrderedDict(sorted(results.items()))

    def has_origin_variables(self) -> bool:
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

        studies = {target_variable.dataset.study for target_variable in target_variables}

        result = OrderedDict()
        for study in studies:
            periods = Period.objects.filter(study_id=study.id).order_by("name").all()
            result[study.name] = OrderedDict()
            for period in periods:
                result[study.name][period.name] = list()
        for target_variable in target_variables:
            study_name = target_variable.dataset.study.name
            period_name = target_variable.get_period(
                period_id="name", default="no period"
            )
            if object_type == "variable":
                result[study_name][period_name].append(target_variable)
            elif object_type == "question":
                result[study_name][
                    period_name
                ] += target_variable.questions_variables.all()
        return result

    def get_target_variables(self):
        """ Return "target variables" i.e. variables that have this variable instance as their "origin" """
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

        studies = {origin_variable.dataset.study for origin_variable in origin_variables}

        result = OrderedDict()
        for study in studies:
            periods = Period.objects.filter(study_id=study.id).order_by("name").all()
            result[study.name] = OrderedDict()
            for period in periods:
                result[study.name][period.name] = list()
        for origin_variable in origin_variables:
            study_name = origin_variable.dataset.study.name
            period_name = origin_variable.get_period(
                period_id="name", default="no period"
            )
            if object_type == "variable":
                result[study_name][period_name].append(origin_variable)
            elif object_type == "question":
                result[study_name][
                    period_name
                ] += origin_variable.questions_variables.all()
        return result

    def get_origin_variables(self):
        """ Return "origin variables" i.e. variables that have this variable instance as their "target" """
        return self.get_origins_by_study_and_period(object_type="variable")

    def get_origin_questions(self):
        """ Return "origin questions" i.e. questions that have this variable instance as their "target" """
        return self.get_origins_by_study_and_period(object_type="question")

    def has_translations(self) -> bool:
        """ Returns True if Variable has translation_languages """
        return len(self.translation_languages()) > 0

    def translation_languages(self) -> List[str]:
        """ Return a list of translation languages """
        if not self.languages:
            members = inspect.getmembers(self)
            self.languages = [
                label[0].replace("label_", "")
                for label in members
                if ("label_" in label[0])
            ]
        return self.languages

    def translation_table(self) -> Dict:
        """ Return a dictionary of languages and translated pairs of "labels" and "categories" """
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
        """ Returns True if the variable has categories """
        return len(self.categories) > 0

    def to_dict(self) -> Dict:
        """ Returns a dictionary representation of the Variable object """
        return dict(
            name=self.name,
            label=self.label,
            label_de=self.label_de,
            concept_id=self.concept_id,
            scale=self.scale,
            uni=self.categories,
        )

    def to_topic_dict(self, language="en") -> Dict:
        """ Returns a topic dictionary representation of the Variable object """

        self.set_language(language)

        # A variable might not have a related concept
        try:
            concept_key = f"concept_{self.concept.name}"
        except AttributeError:
            concept_key = None

        return dict(
            key=f"variable_{self.id}",
            name=self.name,
            title=self.title(),
            concept_key=concept_key,
            type="variable",
        )

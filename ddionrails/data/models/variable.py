# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.data app: Variable """

from __future__ import annotations

import inspect
import logging
import uuid
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Optional, Union

from django.contrib.postgres.fields.jsonb import JSONField as JSONBField
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.functional import cached_property
from filer.fields.image import FilerImageField

from config.helpers import render_markdown
from ddionrails.base.mixins import ModelMixin
from ddionrails.concepts.models import Concept, Period
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.studies.models import Study

from .dataset import Dataset

# Workaround to prevent cyclic importing.
# Refactoring of data and instrument app might be necessary to remove this.
# Exclude this from test coverage since its not related to functionality.
if TYPE_CHECKING:  # pragma: no cover
    from ddionrails.instruments.models.question import Question

LOGGER = logging.getLogger(__name__)


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
    statistics = JSONBField(
        default=dict, null=True, blank=True, help_text="Statistics of the variable(JSON)"
    )
    scale = models.CharField(
        max_length=255, null=True, blank=True, help_text="Scale of the variable"
    )
    categories = JSONBField(
        default=dict, null=True, blank=True, help_text="Categories of the variable(JSON)"
    )

    #############
    # relations #
    #############
    dataset = models.ForeignKey(
        Dataset,
        blank=True,
        null=False,
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
    image = FilerImageField(
        null=True, related_name="variable_image", blank=True, on_delete=models.CASCADE
    )
    image_de = FilerImageField(
        null=True, related_name="variable_image_de", blank=True, on_delete=models.CASCADE
    )

    # Non database attributes
    class Cache(NamedTuple):
        """Cache data received from database."""

        id: uuid.UUID
        content: List[Variable]

    related_cache: Optional[Cache] = None
    languages: List[str] = list()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.dataset_id, self.name, cache=False
        )
        # Disable attribute-defined-outside-init warning.
        # Django magic defines _id fields.
        self.period_id = self.dataset.period_id  # pylint: disable=W0201
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
        return str(
            reverse(
                "data:variable_detail",
                kwargs={
                    "study_name": self.dataset.study.name,
                    "dataset_name": self.dataset.name,
                    "variable_name": self.name,
                },
            )
        )

    @classmethod
    def get(cls, parameters: Dict[str, str]) -> Variable:
        study = get_object_or_404(Study, name=parameters["study_name"])
        dataset = get_object_or_404(Dataset, name=parameters["dataset_name"], study=study)
        variable = get_object_or_404(cls, name=parameters["name"], dataset=dataset)
        return variable

    @classmethod
    def get_by_concept_id(cls, concept_id: int) -> QuerySet:
        """ Return a QuerySet of Variable objects by a given concept id """
        return cls.objects.filter(concept_id=concept_id)

    def html_description(self) -> str:
        """ Return a markdown rendered version of the "description_long" field """
        try:
            html = render_markdown(self.description)
        # The markdown.markdown function used by render markdown can potentially
        # raise these errors. But I did not find any input, that triggered errors.
        # They also exclude these except blocks from coverage themselves.
        except UnicodeDecodeError:  # pragma: no cover
            LOGGER.debug("Encoding error in long description: %s", self.description_long)
            html = ""
        except ValueError:  # pragma: no cover
            LOGGER.debug(
                "Cannot perform basic string operations on long description: %s",
                self.description_long,
            )
            html = ""
        return html

    def get_categories(self) -> List[Dict[str, str]]:
        """ Return a list of dictionaries based on the "categories" field """
        if self.categories:
            categories = []
            if "labels_de" not in self.categories:
                self.categories["labels_de"] = self.categories["labels"]
            for index, _ in enumerate(self.categories["values"]):
                category = dict(
                    value=self.categories["values"][index],
                    label=self.categories["labels"][index],
                    frequency=self.categories["frequencies"][index],
                    valid=(not self.categories["missings"][index]),
                    label_de=self.categories["labels_de"][index],
                )
                categories.append(category)
            return categories

        return []

    def get_study(self, study_id: bool = False) -> Union[Study, uuid.UUID]:
        """ Returns the related study_id | Study instance """
        if study_id:
            return self.dataset.study.id
        return self.dataset.study

    def get_concept(self, default=None, concept_id=False):
        """ Returns the related concept_id | Concept instance | a default """
        if self.concept:
            if concept_id:
                return self.concept.id
            return self.concept
        return default

    @property
    def period_fallback(self):
        """Retrieve period from dataset if variable period is not set yet."""
        if self.period:
            return self.period
        return self.dataset.period

    def get_related_variables(self) -> Union[List, QuerySet]:
        """ Returns the related variables by concept """
        # Only update if cache is empty or
        # if concept has changed.
        if self.related_cache is None or self.related_cache.id != getattr(
            self.concept, "id", None
        ):
            if self.concept:
                variables = Variable.objects.select_related(
                    "dataset", "dataset__study", "period"
                ).filter(concept=self.concept, dataset__study=self.dataset.study)
                self.related_cache = self.Cache(id=self.concept.id, content=variables)
            else:
                self.related_cache = None
        return getattr(self.related_cache, "content", list())

    def get_related_variables_by_period(self) -> OrderedDict:
        """ Returns the related variables by concept, ordered by period """
        results = dict()
        periods = Period.objects.filter(study_id=self.dataset.study.id).all()
        period_names = self._period_model_to_name_dict(periods)
        results = {period_name: list() for period_name in period_names.values()}
        results["none"] = list()
        for variable in self.get_related_variables():
            try:
                results[period_names[variable.period_id]].append(variable)
            except KeyError:
                results["none"].append(variable)
        if not results["none"]:
            del results["none"]
        return OrderedDict(sorted(results.items()))

    @staticmethod
    def _period_model_to_name_dict(instances: List[Period]) -> Dict[Dict[str, Any]]:
        return {instance.id: instance.name for instance in instances}

    @staticmethod
    def _get_related_variable_information(
        objects: Union[List[Variable], List[Question]]
    ) -> Dict[str, Dict[str, List[Variable]]]:
        """Get objects related through transformations

        Notice: The following is my own best interpretation at the moment.
        This code was contained both in get_targets_by_study_and_period
        and get_origin_by_study_and_period.
        Its purpose seems to be, to get information to display it on on the
        variable page.
        Specifically to retrieve the periods of related variables or questions and put
        everything together into a dict.
        The dictionary content is used by a template.

        The periods are kept in an OrderedDict so that they can be displayed as
        such on the variable page.

        Params:
            objects: Variables or Objects related to this variable instance.
            object_type: The type of the input. Either variable or question.
        """

        studies = {variable.dataset.study for variable in objects}

        # TODO: Change when OrderedDict typing becomes available. pylint: disable=W0511
        result: Dict[str, Dict[str, List[Variable]]] = OrderedDict()
        for study in studies:
            periods = Period.objects.filter(study_id=study.id).order_by("name").all()
            result[study.name] = OrderedDict()
            for period in periods:
                result[study.name][period.name] = list()
        for _objects in objects:
            study_name = _objects.dataset.study.name
            period = getattr(_objects, "period_fallback", None)
            period_name = getattr(period, "name", "no period")
            result[study_name][period_name].append(_objects)
        return result

    @cached_property
    def target_variables_dict(self):
        """
        Get objects that are based on an relationship through transformations
        in the direction to target (e.g., all wide variables, which a long
        variable is based on).

        Target variables are those,
        that that have this variable instance as their "origin"
        :return: Nested dicts, study --> period --> list of variables/questions
        """
        target_variables = [x.target for x in self.target_variables.all()]
        return self._get_related_variable_information(target_variables)

    @cached_property
    def origin_variables_dict(self):
        """
        Get objects that are based on an relationship through transformations
        in the direction to origin (e.g., all wide variables, which a long
        variable is based on).

        Origin variables are those that have this variable instance as their "target"

        :return: Nested dicts, study --> period --> list of variables/questions
        """
        origin_variables = [x.origin for x in self.origin_variables.all()]
        return self._get_related_variable_information(origin_variables)

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
        """Get labels and categories in their available languages."""
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
        # This is too much of a guess.
        # Variables can have labels denoting missing values, even if they are
        # not categorical.
        return len(self.categories) > 0

    @property
    def content_dict(self) -> Dict:
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
        concept_key: Optional[str]
        if self.concept:
            concept_key = f"concept_{self.concept.name}"
        else:
            concept_key = None

        return dict(
            key=f"variable_{self.id}",
            name=self.name,
            title=self.title(),
            concept_key=concept_key,
            type="variable",
        )

    def __lt__(self, variable: Variable) -> bool:
        """Determine relation of variables according to their name."""
        if not isinstance(variable, Variable):
            raise TypeError(
                "'<' not supported between instances of {} and {}".format(
                    type(self), type(variable)
                )
            )
        return self.name < variable.name

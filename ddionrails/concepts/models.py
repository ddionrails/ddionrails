# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.concepts app """

from __future__ import annotations

import uuid
from typing import List

from django.db import models
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin
from ddionrails.imports.helpers import hash_with_base_uuid, hash_with_namespace_uuid
from ddionrails.studies.models import Study


class Topic(models.Model, ModelMixin):
    """
    Stores a single topic,
    related to :model:`studies.Study` and :model:`concepts.Topic`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the Topic. Dependent on the associated study",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        unique=False,
        help_text="Name of the topic (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the topic (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the topic (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the topic (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the topic (Markdown, German)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="topics",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )
    parent = models.ForeignKey(
        "self",
        related_name="children",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Parent (concepts.Topic)",
        help_text="Foreign key to concepts.Topic",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.study_id, self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "parent"]

    @staticmethod
    def get_children(topic_id: int) -> List[Topic]:
        """ Returns a list of all Topics, that have this Topic object as its ancestor """
        children = list(Topic.objects.filter(parent_id=topic_id).all())
        for child in children:
            children += list(Topic.get_children(child.id))
        return children

    @staticmethod
    def get_topic_tree_leaves(
        topic_object: Topic = None, topic_id: uuid.UUID = ""
    ) -> List[Topic]:
        """Get all ancestor Topics with no further child topics.

        Works recursively similar to get_children but does not return
        intermediate Topics.
        """
        if topic_object:
            children = list(Topic.objects.filter(parent=topic_object).all())
        elif topic_id:
            children = list(Topic.objects.filter(parent_id=topic_id).all())
            topic_object = Topic.objects.get(id=topic_id)
        else:
            return []
        if not children:
            return [topic_object]

        grand_children = list()
        for child in children:
            grand_children += list(Topic.get_topic_tree_leaves(topic_object=child))
        return grand_children


class Concept(ModelMixin, models.Model):
    """
    Stores a single concept,
    related to :model:`data.Variable`,
    :model:`concepts.Topic` and :model:`instruments.ConceptQuestion`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the Concept.",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        unique=True,
        db_index=True,
        verbose_name="concept name",
        help_text="Name of the concept (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the concept (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the concept (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the concept (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the concept (Markdown, German)",
    )

    #############
    # relations #
    #############
    topics = models.ManyToManyField(
        Topic, related_name="concepts", help_text="ManyToMany relation to concepts.Topic"
    )

    class DOR(ModelMixin.DOR):  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["name"]
        io_fields = ["name", "label", "description"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/concept/{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save().

        The creation of the value set for the id field is different than
        for most other models. Concepts are, like studies, not inside the
        namespace of any other object, meaning the uuid is derived from
        the overall base uuid. This could cause a collision of uuids, if
        a Concept shares a name with a study. While this seems unlikely to
        happen, it is circumvented by concatenating each name with the
        literal string `concept:`.
        """
        self.id = hash_with_base_uuid(  # pylint: disable=C0103
            "concept:" + self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "name" field """
        return reverse("concepts:concept_detail_name", kwargs={"concept_name": self.name})


class Period(models.Model, ModelMixin):
    """
    Stores a single period,
    related to :model:`studies.Study`.

    Periods define time references.

    For the definition, use one of the following formats:

    -   Year: ``2011``
    -   Month: ``2011-05``
    -   Date: ``2011-05-03``
    -   Range: ``2010-01:2011-12``
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the Period. Dependent on the associated Study.",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        help_text="Name of the period (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the period (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the period (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the period (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the period (Markdown, German)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="periods",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "definition"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/period/{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.study_id, self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class AnalysisUnit(models.Model, ModelMixin):
    """
    Stores a single analysis unit.

    Analysis units refer to real world objects.

    * p = individual (person)
    * h = household
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the AnalysisUnit.",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        help_text="Name of the analysis unit (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the analysis unit (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the analysis unit (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the analysis unit (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the analysis unit (Markdown, German)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="analysis_units",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ("study", "name")

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/analysis_unit/{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save()."""
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.study_id, self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class ConceptualDataset(models.Model, ModelMixin):
    """
    Stores a single conceptual dataset.

    Conceptual datasets group datasets.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the ConceptualDataset.",
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        help_text="Name of the conceptual dataset (Lowercase)",
    )
    label = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (English)",
        help_text="Label of the conceptual dataset (English)",
    )
    label_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Label (German)",
        help_text="Label of the conceptual dataset (German)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, English)",
        help_text="Description of the conceptual dataset (Markdown, English)",
    )
    description_de = models.TextField(
        blank=True,
        verbose_name="Description (Markdown, German)",
        help_text="Description of the conceptual dataset (Markdown, German)",
    )

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="conceptual_datasets",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        id_fields = ("study", "name")

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/conceptual_dataset/{self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Set id and call parents save()."""
        self.id = hash_with_namespace_uuid(  # pylint: disable=C0103
            self.study_id, self.name, cache=False
        )
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

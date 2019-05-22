# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.concepts app """

from django.db import models
from django.urls import reverse

from config.validators import validate_lowercase
from ddionrails.base.mixins import ModelMixin
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin
from ddionrails.studies.models import Study


class Topic(models.Model, ModelMixin, ElasticMixin):
    """
    Stores a single topic,
    related to :model:`studies.Study` and :model:`concepts.Topic`.
    """

    # attributes
    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        unique=True,
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
        verbose_name="Description (Markdown)",
        help_text="Description of the topic (Markdown)",
    )

    # relations
    study = models.ForeignKey(
        Study, on_delete=models.CASCADE, help_text="Foreign key to studies.Study"
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

    class Meta:
        """ Django's metadata options """

        unique_together = ("study", "name")

    class DOR:
        """ ddionrails' metadata options """

        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "parent"]

    @classmethod
    def get_children(cls, topic_id):
        children = list(cls.objects.filter(parent_id=topic_id).all())
        for child in children:
            children += list(cls.get_children(child.id))
        return children


class Concept(models.Model, ModelMixin, ElasticMixin):
    """
    Stores a single concept,
    related to :model:`data.Variable`, :model:`concepts.Topic` and :model:`instruments.ConceptQuestion`.
    """

    # attributes
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
        verbose_name="Description (Markdown)",
        help_text="Description of the concept (Markdown)",
    )

    # relations
    topics = models.ManyToManyField(
        Topic, related_name="concepts", help_text="ManyToMany relation to concepts.Topic"
    )

    DOC_TYPE = "concept"

    class DOR(ModelMixin.DOR):
        """ ddionrails' metadata options """

        id_fields = ["name"]
        io_fields = ["name", "label", "description"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/concept/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "name" field """
        return reverse("concepts:concept_detail_name", kwargs={"concept_name": self.name})

    def index(self) -> None:
        """ Indexes the concept in Elasticsearch (name, label and related study) """
        if self.label and self.label != "":
            label = self.label
        else:
            try:
                label = self.variables.first().label
            except AttributeError:
                label = ""
        study = list(
            set(
                [
                    s.name
                    for s in Study.objects.filter(
                        datasets__variables__concept_id=self.id
                    ).all()
                ]
            )
        )
        self.set_elastic(dict(name=self.name, label=label, study=study))

    @classmethod
    def index_all(cls) -> None:
        """ Indexes all concepts in Elasticsearch using the index method """
        for concept in cls.objects.all():
            concept.index()


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

    # attributes
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
    description = models.TextField(
        blank=True,
        verbose_name="Description (Markdown)",
        help_text="Description of the period (Markdown)",
    )
    definition = models.CharField(
        max_length=255, blank=True, help_text="Definition of the period"
    )

    # relations
    study = models.ForeignKey(
        Study,
        related_name="periods",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    class Meta:
        """ Django's metadata options """

        unique_together = ("study", "name")

    class DOR:
        """ ddionrails' metadata options """

        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "definition"]

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/period/{self.name}"

    def title(self) -> str:
        """ Returns a title representation using the "label" field, with "name" field as fallback """
        return str(self.label) if self.label != "" else str(self.name)

    def is_range(self) -> bool:
        """ Returns if "definition" defines a range """
        return ":" in self.definition


class AnalysisUnit(models.Model, ModelMixin):
    """
    Stores a single analysis unit.

    Analysis units refer to real world objects.

    * p = individual (person)
    * h = household
    """

    name = models.CharField(
        max_length=255,
        unique=True,
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
        verbose_name="Description (Markdown)",
        help_text="Description of the analysis unit (Markdown)",
    )

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/analysis_unit/{self.name}"

    def title(self) -> str:
        """ Returns a title representation using the "label" field, with "name" field as fallback """
        return str(self.label) if self.label != "" else str(self.name)


class ConceptualDataset(models.Model, ModelMixin):
    """
    Stores a single conceptual dataset.

    Conceptual datasets group datasets.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
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
        verbose_name="Description (Markdown)",
        help_text="Description of the conceptual dataset (Markdown)",
    )

    def __str__(self) -> str:
        """ Returns a string representation using the "name" field """
        return f"/conceptual_dataset/{self.name}"

    def title(self) -> str:
        """ Returns a title representation using the "label" field, with "name" field as fallback """
        return str(self.label) if self.label != "" else str(self.name)

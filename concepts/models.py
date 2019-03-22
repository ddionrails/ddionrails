from django.db import models
from django.urls import reverse

from ddionrails.mixins import ModelMixin
from ddionrails.validators import validate_lowercase
from elastic.mixins import ModelMixin as ElasticMixin
from studies.models import Study


class Topic(models.Model, ModelMixin, ElasticMixin):

    name = models.CharField(max_length=255, validators=[validate_lowercase], unique=True)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", related_name="children", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("study", "name")

    class DOR:
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
    related to :model:`data.Variable` and :model:`instruments.ConceptQuestion`.
    """

    name = models.CharField(
        max_length=255,
        validators=[validate_lowercase],
        unique=True,
        db_index=True,
        verbose_name="concept name",
        help_text="Name of the concept.",
    )
    label = models.CharField(
        max_length=255, blank=True, help_text="Label (English) of the concept."
    )
    description = models.TextField(
        blank=True, help_text="Description of the concept using Markdown."
    )
    topics = models.ManyToManyField(Topic, related_name="concepts")

    DOC_TYPE = "concept"

    class DOR(ModelMixin.DOR):
        id_fields = ["name"]
        io_fields = ["name", "label", "description"]

    def __str__(self):
        """ Returns a string representation of the concept using its name """
        return "/concept/%s" % self.name

    def get_absolute_url(self):
        return reverse("concepts:concept_detail_name", kwargs={"concept_name": self.name})

    def index(self):
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
    def index_all(cls):
        """ Indexes all concepts in Elasticsearch using the index method """
        for concept in cls.objects.all():
            concept.index()


class Period(models.Model, ModelMixin):
    """
    Periods define time references.

    For the definition, use one of the following formats:

    -   Year: ``2011``
    -   Month: ``2011-05``
    -   Date: ``2011-05-03``
    -   Range: ``2010-01:2011-12``
    """

    study = models.ForeignKey(Study, related_name="periods", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, validators=[validate_lowercase])
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    definition = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("study", "name")

    class DOR:
        id_fields = ["study", "name"]
        io_fields = ["study", "name", "label", "description", "definition"]

    def title(self):
        return self.label if self.label != "" else self.name

    def is_range(self):
        return ":" in self.definition

    def __str__(self):
        return "/period/%s" % self.name


class AnalysisUnit(models.Model, ModelMixin):
    """
    Analysis units refer to real world objects.

    * p = individual (person)
    * h = household
    """

    name = models.CharField(max_length=255, unique=True, validators=[validate_lowercase])
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def title(self):
        return self.label if self.label != "" else self.name

    def __str__(self):
        return "/analysis_unit/%s" % self.name


class ConceptualDataset(models.Model, ModelMixin):
    """
    Conceptual datasets group datasets.
    """

    name = models.CharField(max_length=255, unique=True, validators=[validate_lowercase])
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def title(self):
        return self.label if self.label != "" else self.name

    def __str__(self):
        return "/conceptual_dataset/%s" % self.name

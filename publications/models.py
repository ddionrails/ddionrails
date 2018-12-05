from django.db import models
from django.urls import reverse

from ddionrails.mixins import ModelMixin as DorMixin
from elastic.mixins import ModelMixin as ElasticMixin
from studies.models import Study


class Publication(ElasticMixin, DorMixin, models.Model):
    """
    Publication from BibTeX import.
    """

    name = models.CharField(max_length=255, db_index=True)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    study = models.ForeignKey(Study, blank=True, null=True, related_name="publications", on_delete=models.CASCADE)

    DOC_TYPE = "publication"

    class Meta:
        unique_together = ("study", "name")

    def __str__(self):
        return "%s/publ/%s" % (self.study, self.name)

    def get_absolute_url(self):
        return reverse("publ:publication", kwargs={"study_name": self.study.name, "publication_name": self.name})

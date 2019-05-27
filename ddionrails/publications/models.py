# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.publications app """

from typing import Dict

from django.db import models
from django.urls import reverse

from config.helpers import render_markdown
from ddionrails.base.mixins import ModelMixin as DorMixin
from ddionrails.data.models import Dataset, Variable
from ddionrails.elastic.mixins import ModelMixin as ElasticMixin
from ddionrails.instruments.models import Instrument, Question
from ddionrails.studies.models import Study


class Publication(ElasticMixin, DorMixin, models.Model):
    """
    Stores a single publication, related to :model:`studies.Study`.
    """

    # attributes
    name = models.CharField(
        max_length=255, db_index=True, help_text="Name of the publication"
    )
    sub_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="Type of the publication (e.g., journal article or dissertation)",
    )
    title = models.TextField(blank=True, help_text="Title of the publication")
    author = models.TextField(blank=True, help_text="Name(s) of the author(s)")
    year = models.TextField(blank=True, help_text="Year of publication")
    abstract = models.TextField(blank=True, help_text="Abstract of the publication")
    cite = models.TextField(blank=True, help_text="Suggested citation of the publication")
    url = models.TextField(
        blank=True, verbose_name="URL", help_text="URL referencing the publication"
    )
    doi = models.TextField(
        blank=True,
        verbose_name="DOI",
        help_text="DOI of the publication (DOI only, not the URL to the DOI)",
    )
    studies = models.TextField(
        blank=True,
        help_text="Description of studies/data sources used in the publication",
    )

    # relations
    study = models.ForeignKey(
        Study,
        blank=True,
        null=True,
        related_name="publications",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    # Used by ElasticMixin when indexed into Elasticsearch
    DOC_TYPE = "publication"

    class Meta:
        """ Django's metadata options """

        unique_together = ("study", "name")

    def __str__(self) -> str:
        """ Returns a string representation using the "study" and "name" fields """
        return f"{self.study}/publ/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse(
            "publ:publication",
            kwargs={"study_name": self.study.name, "publication_name": self.name},
        )

    def html_abstract(self) -> str:
        """ Returns the "abstract" field as a string containing HTML markup """
        return render_markdown(self.abstract)

    def html_cite(self) -> str:
        """ Returns the "cite" field as a string containing HTML markup """
        return render_markdown(self.cite)

    def to_elastic_dict(self) -> Dict[str, str]:
        """ Returns a dictionary to be indexed by Elasticsearch """
        try:
            study_name = self.study.name
        except AttributeError:
            study_name = ""
        return dict(
            name=self.name,
            sub_type=self.sub_type,
            title=self.title,
            author=self.author,
            year=self.year,
            period=self.year,
            abstract=self.abstract,
            cite=self.cite,
            url=self.url,
            doi=self.doi,
            study=study_name,
        )


class Attachment(models.Model):
    """
    Stores a single attachment, related to:
    :model:`studies.Study`,
    :model:`data.Dataset`,
    :model:`data.Variable`,
    :model:`instruments.Instrument` and
    :model:`instruments.Question`

    """

    # attributes
    url = models.TextField(
        blank=True, verbose_name="URL", help_text="Link (URL) to the attachment"
    )
    url_text = models.TextField(
        blank=True, verbose_name="URL text", help_text="Text to be displayed for the link"
    )

    # relations
    context_study = models.ForeignKey(
        Study,
        related_name="related_attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )
    study = models.ForeignKey(
        Study,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )
    dataset = models.ForeignKey(
        Dataset,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Dataset",
    )
    variable = models.ForeignKey(
        Variable,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
    )
    instrument = models.ForeignKey(
        Instrument,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to instruments.Instrument",
    )
    question = models.ForeignKey(
        Question,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="Foreign key to instruments.Question",
    )

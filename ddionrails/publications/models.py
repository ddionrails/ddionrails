# -*- coding: utf-8 -*-
""" Model definitions for ddionrails.publications app """

import uuid

from django.db import models
from django.urls import reverse

from config.helpers import render_markdown
from ddionrails.base.mixins import ModelMixin
from ddionrails.data.models import Dataset, Variable
from ddionrails.imports.helpers import hash_with_namespace_uuid
from ddionrails.instruments.models import Instrument, Question
from ddionrails.studies.models import Study


class Publication(ModelMixin, models.Model):
    """
    Stores a single publication, related to :model:`studies.Study`.
    """

    ##############
    # attributes #
    ##############
    id = models.UUIDField(  # pylint: disable=C0103
        primary_key=True,
        default=uuid.uuid4,
        editable=True,
        db_index=True,
        help_text="UUID of the publication. Dependent on the associated study.",
    )
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
    year = models.PositiveSmallIntegerField(
        blank=True, null=True, help_text="Year of publication"
    )
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

    #############
    # relations #
    #############
    study = models.ForeignKey(
        Study,
        related_name="publications",
        on_delete=models.CASCADE,
        help_text="Foreign key to studies.Study",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """"Set id and call parents save(). """
        self.id = hash_with_namespace_uuid(
            self.study_id, self.name, cache=False
        )  # pylint: disable=C0103
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        unique_together = ("study", "name")

    def __str__(self) -> str:
        """ Returns a string representation using the "study" and "name" fields """
        return f"{self.study}/publ/{self.name}"

    def get_absolute_url(self) -> str:
        """ Returns a canonical URL for the model using the "study" and "name" fields """
        return reverse(
            "publ:publication_detail",
            kwargs={"study_name": self.study.name, "publication_name": self.name},
        )

    def html_abstract(self) -> str:
        """ Returns the "abstract" field as a string containing HTML markup """
        return render_markdown(self.abstract)

    def html_cite(self) -> str:
        """ Returns the "cite" field as a string containing HTML markup """
        return render_markdown(self.cite)


class Attachment(models.Model):
    """
    Stores a single attachment, related to:
    :model:`studies.Study`,
    :model:`data.Dataset`,
    :model:`data.Variable`,
    :model:`instruments.Instrument` and
    :model:`instruments.Question`

    """

    ##############
    # attributes #
    ##############
    url = models.TextField(
        blank=True, verbose_name="URL", help_text="Link (URL) to the attachment"
    )
    url_text = models.TextField(
        blank=True, verbose_name="URL text", help_text="Text to be displayed for the link"
    )

    #############
    # relations #
    #############
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

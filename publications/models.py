from django.db import models
from django.urls import reverse

from concepts.models import Period
from data.models import Dataset, Variable
from ddionrails.helpers import render_markdown
from ddionrails.mixins import ModelMixin as DorMixin
from elastic.mixins import ModelMixin as ElasticMixin
from instruments.models import Instrument, Question
from studies.models import Study


class Publication(ElasticMixin, DorMixin, models.Model):
    """
    Publication model
    """

    name = models.CharField(max_length=255, db_index=True)
    sub_type = models.CharField(max_length=255, blank=True)
    title = models.TextField(blank=True)
    author = models.TextField(blank=True)
    date = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    cite = models.TextField(blank=True)
    url = models.TextField(blank=True)

    period = models.ForeignKey(Period, blank=True, null=True, on_delete=models.CASCADE)
    study = models.ForeignKey(
        Study,
        blank=True,
        null=True,
        related_name="publications",
        on_delete=models.CASCADE,
    )

    DOC_TYPE = "publication"

    class Meta:
        unique_together = ("study", "name")

    def html_abstract(self):
        return render_markdown(self.abstract)

    def html_cite(self):
        return render_markdown(self.cite)

    def to_elastic_dict(self):
        try:
            study_name = self.study.name
        except:
            study_name = ""
        try:
            period_name = self.period.name
        except:
            period_name = ""
        return dict(
            name=self.name,
            sub_type=self.sub_type,
            title=self.title,
            author=self.author,
            date=self.date,
            abstract=self.abstract,
            cite=self.cite,
            url=self.url,
            period=period_name,
            study=study_name,
        )

    def __str__(self):
        return "%s/publ/%s" % (self.study, self.name)

    def get_absolute_url(self):
        return reverse(
            "publ:publication",
            kwargs={"study_name": self.study.name, "publication_name": self.name},
        )


class Attachment(models.Model):

    context_study = models.ForeignKey(
        Study, related_name="related_attachments", on_delete=models.CASCADE
    )
    study = models.ForeignKey(
        Study, blank=True, null=True, related_name="attachments", on_delete=models.CASCADE
    )
    dataset = models.ForeignKey(
        Dataset,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    variable = models.ForeignKey(
        Variable,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    instrument = models.ForeignKey(
        Instrument,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        Question,
        blank=True,
        null=True,
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    url = models.TextField(blank=True)
    url_text = models.TextField(blank=True)

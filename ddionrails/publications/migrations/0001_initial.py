# Generated by Django 2.2.3 on 2019-07-19 14:05
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# Pylint is not fully compatible with isort
# pylint: disable=ungrouped-imports

import uuid

import django.db.models.deletion
from django.db import migrations, models

import ddionrails.base.mixins
import ddionrails.elastic.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("instruments", "0001_initial"),
        ("studies", "0001_initial"),
        ("data", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "url",
                    models.TextField(
                        blank=True,
                        help_text="Link (URL) to the attachment",
                        verbose_name="URL",
                    ),
                ),
                (
                    "url_text",
                    models.TextField(
                        blank=True,
                        help_text="Text to be displayed for the link",
                        verbose_name="URL text",
                    ),
                ),
                (
                    "context_study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_attachments",
                        to="studies.Study",
                    ),
                ),
                (
                    "dataset",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to data.Dataset",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="data.Dataset",
                    ),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to instruments.Instrument",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="instruments.Instrument",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to instruments.Question",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="instruments.Question",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to studies.Study",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="studies.Study",
                    ),
                ),
                (
                    "variable",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to data.Variable",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="data.Variable",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text=(
                            "UUID of the publication. Dependent on the associated study."
                        ),
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, help_text="Name of the publication", max_length=255
                    ),
                ),
                (
                    "sub_type",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Type of the publication "
                            "(e.g., journal article or dissertation)"
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "title",
                    models.TextField(blank=True, help_text="Title of the publication"),
                ),
                (
                    "author",
                    models.TextField(blank=True, help_text="Name(s) of the author(s)"),
                ),
                ("year", models.TextField(blank=True, help_text="Year of publication")),
                (
                    "abstract",
                    models.TextField(blank=True, help_text="Abstract of the publication"),
                ),
                (
                    "cite",
                    models.TextField(
                        blank=True, help_text="Suggested citation of the publication"
                    ),
                ),
                (
                    "url",
                    models.TextField(
                        blank=True,
                        help_text="URL referencing the publication",
                        verbose_name="URL",
                    ),
                ),
                (
                    "doi",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "DOI of the publication (DOI only, not the URL to the DOI)"
                        ),
                        verbose_name="DOI",
                    ),
                ),
                (
                    "studies",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Description of studies/data sources used in the publication"
                        ),
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="publications",
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(
                ddionrails.elastic.mixins.ModelMixin,
                ddionrails.base.mixins.ModelMixin,
                models.Model,
            ),
        ),
    ]

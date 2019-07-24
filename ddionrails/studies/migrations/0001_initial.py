# Generated by Django 2.2.4 on 2019-08-13 14:17
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# Pylint is not fully compatible with isort
# pylint: disable=ungrouped-imports

# Help texts are often too long here but this file is not meant for reading
# anyways. The models themselves are, the lines there follow the 90 char limit.
# pylint: disable=line-too-long

import uuid

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models

import ddionrails.base.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Study",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="UUID of the study",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="Name of the study",
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the study (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the study (German)",
                        max_length=255,
                        null=True,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the study (Markdown, English)",
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text="Description of the study (Markdown, German)",
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "doi",
                    models.CharField(
                        blank=True,
                        help_text="DOI of the study (DOI only, not the URL to the DOI)",
                        max_length=255,
                        verbose_name="DOI",
                    ),
                ),
                (
                    "repo",
                    models.CharField(
                        blank=True,
                        help_text="Reference to the Git repository without definition of the protocol (e.g. https)",
                        max_length=255,
                    ),
                ),
                (
                    "current_commit",
                    models.CharField(
                        blank=True,
                        help_text="Commit hash of the last metadata import. This field is automatically filled by DDI on Rails",
                        max_length=255,
                    ),
                ),
                (
                    "config",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Configuration of the study (JSON)",
                        null=True,
                    ),
                ),
                (
                    "topic_languages",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=200),
                        blank=True,
                        default=list,
                        help_text="Topic languages of the study (Array)",
                        size=None,
                    ),
                ),
            ],
            options={"verbose_name_plural": "Studies"},
            bases=(
                ddionrails.base.mixins.ImportPathMixin,
                ddionrails.base.mixins.ModelMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="TopicList",
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
                    "topiclist",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default=list,
                        help_text="Topics of the related study (JSON)",
                        null=True,
                    ),
                ),
                (
                    "study",
                    models.OneToOneField(
                        blank=True,
                        help_text="OneToOneField to studies.Study",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="topiclist",
                        to="studies.Study",
                    ),
                ),
            ],
        ),
    ]

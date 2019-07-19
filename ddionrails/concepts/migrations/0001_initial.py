# Generated by Django 2.2.3 on 2019-07-19 14:05
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# Pylint is not fully compatible with isort
# pylint: disable=ungrouped-imports

import uuid

import django.db.models.deletion
from django.db import migrations, models

import config.validators
import ddionrails.base.mixins
import ddionrails.elastic.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [("studies", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="UUID of the Topic. Dependent on the associated study",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the topic (Lowercase)",
                        max_length=255,
                        unique=True,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the topic (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the topic (German)",
                        max_length=255,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the topic (Markdown, English)",
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text="Description of the topic (Markdown, German)",
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        help_text="Foreign key to concepts.Topic",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="concepts.Topic",
                        verbose_name="Parent (concepts.Topic)",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(models.Model, ddionrails.base.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name="Concept",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="UUID of the Concept.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True,
                        help_text="Name of the concept (Lowercase)",
                        max_length=255,
                        unique=True,
                        validators=[config.validators.validate_lowercase],
                        verbose_name="concept name",
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the concept (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the concept (German)",
                        max_length=255,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the concept (Markdown, English)",
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text="Description of the concept (Markdown, German)",
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "topics",
                    models.ManyToManyField(
                        help_text="ManyToMany relation to concepts.Topic",
                        related_name="concepts",
                        to="concepts.Topic",
                    ),
                ),
            ],
            bases=(
                models.Model,
                ddionrails.base.mixins.ModelMixin,
                ddionrails.elastic.mixins.ModelMixin,
            ),
        ),
        migrations.CreateModel(
            name="Period",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text=(
                            "UUID of the Period. Dependent on the associated Study."
                        ),
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the period (Lowercase)",
                        max_length=255,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the period (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the period (German)",
                        max_length=255,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the period (Markdown, English)",
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text="Description of the period (Markdown, German)",
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periods",
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(models.Model, ddionrails.base.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name="ConceptualDataset",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="UUID of the ConceptualDataset.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the conceptual dataset (Lowercase)",
                        max_length=255,
                        unique=True,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the conceptual dataset (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the conceptual dataset (German)",
                        max_length=255,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Description of the conceptual dataset (Markdown, English)"
                        ),
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text=(
                            "Description of the conceptual dataset (Markdown, German)"
                        ),
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conceptual_datasets",
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(models.Model, ddionrails.base.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name="AnalysisUnit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text="UUID of the AnalysisUnit.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the analysis unit (Lowercase)",
                        max_length=255,
                        unique=True,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Label of the analysis unit (English)",
                        max_length=255,
                        verbose_name="Label (English)",
                    ),
                ),
                (
                    "label_de",
                    models.CharField(
                        blank=True,
                        help_text="Label of the analysis unit (German)",
                        max_length=255,
                        verbose_name="Label (German)",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Description of the analysis unit (Markdown, English)",
                        verbose_name="Description (Markdown, English)",
                    ),
                ),
                (
                    "description_de",
                    models.TextField(
                        blank=True,
                        help_text="Description of the analysis unit (Markdown, German)",
                        verbose_name="Description (Markdown, German)",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        help_text="Foreign key to studies.Study",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analysis_units",
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(models.Model, ddionrails.base.mixins.ModelMixin),
        ),
    ]

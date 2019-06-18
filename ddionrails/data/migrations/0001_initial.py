# Generated by Django 2.2 on 2019-04-09 07:57

import django.db.models.deletion
from django.db import migrations, models

import config.validators
import ddionrails.base.mixins
import ddionrails.elastic.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [("studies", "__first__"), ("concepts", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Dataset",
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
                    "name",
                    models.CharField(
                        db_index=True,
                        max_length=255,
                        validators=[config.validators.validate_lowercase],
                    ),
                ),
                ("label", models.CharField(blank=True, max_length=255)),
                ("label_de", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField(blank=True)),
                ("boost", models.FloatField(blank=True, null=True)),
                (
                    "analysis_unit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datasets",
                        to="concepts.AnalysisUnit",
                    ),
                ),
                (
                    "conceptual_dataset",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datasets",
                        to="concepts.ConceptualDataset",
                    ),
                ),
                (
                    "period",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datasets",
                        to="concepts.Period",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datasets",
                        to="studies.Study",
                    ),
                ),
            ],
            options={"unique_together": {("study", "name")}},
            bases=(ddionrails.base.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Variable",
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
                ("name", models.CharField(db_index=True, max_length=255)),
                ("label", models.CharField(blank=True, max_length=255)),
                ("label_de", models.CharField(blank=True, max_length=255, null=True)),
                ("description", models.TextField(blank=True)),
                ("description_long", models.TextField(blank=True)),
                ("sort_id", models.IntegerField(blank=True, null=True)),
                ("image_url", models.TextField(blank=True)),
                (
                    "concept",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variables",
                        to="concepts.Concept",
                    ),
                ),
                (
                    "dataset",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variables",
                        to="data.Dataset",
                    ),
                ),
                (
                    "period",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variables",
                        to="concepts.Period",
                    ),
                ),
            ],
            options={"unique_together": {("name", "dataset")}},
            bases=(
                ddionrails.elastic.mixins.ModelMixin,
                ddionrails.base.mixins.ModelMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="Transformation",
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
                    "origin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="target_variables",
                        to="data.Variable",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="origin_variables",
                        to="data.Variable",
                    ),
                ),
            ],
            options={"unique_together": {("origin", "target")}},
        ),
    ]

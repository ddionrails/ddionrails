# Generated by Django 2.2.3 on 2019-07-19 14:05
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# Pylint is not fully compatible with isort
# pylint: disable=ungrouped-imports

from django.db import migrations, models

import ddionrails.base.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="System",
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
                ("current_commit", models.CharField(blank=True, max_length=255)),
            ],
            bases=(ddionrails.base.mixins.ImportPathMixin, models.Model),
        )
    ]

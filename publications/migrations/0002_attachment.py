# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instruments", "0002_auto_20161018_1404"),
        ("data", "0007_auto_20180926_1719"),
        ("studies", "0004_auto_20180926_1719"),
        ("publications", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                ("id", models.AutoField(verbose_name="ID", primary_key=True, serialize=False, auto_created=True)),
                ("url", models.TextField(blank=True)),
                ("url_text", models.TextField(blank=True)),
                (
                    "dataset",
                    models.ForeignKey(
                        blank=True, null=True, related_name="attachments", to="data.Dataset", on_delete=models.CASCADE
                    ),
                ),
                (
                    "instrument",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        related_name="attachments",
                        to="instruments.Instrument",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        related_name="attachments",
                        to="instruments.Question",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True, null=True, related_name="attachments", to="studies.Study", on_delete=models.CASCADE
                    ),
                ),
                (
                    "variable",
                    models.ForeignKey(
                        blank=True, null=True, related_name="attachments", to="data.Variable", on_delete=models.CASCADE
                    ),
                ),
            ],
        )
    ]

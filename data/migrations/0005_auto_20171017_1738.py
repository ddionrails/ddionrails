# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_dataset_boost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='boost',
            field=models.FloatField(null=True, blank=True),
        ),
    ]

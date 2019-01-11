# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instruments', '0002_auto_20161018_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='label_de',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0003_script'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='label',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

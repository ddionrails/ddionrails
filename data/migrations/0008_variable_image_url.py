# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20180926_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='image_url',
            field=models.TextField(blank=True),
        ),
    ]

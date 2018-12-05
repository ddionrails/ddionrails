# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20170516_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='boost',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]

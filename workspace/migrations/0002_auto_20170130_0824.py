# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
        ('workspace', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='release',
        ),
        migrations.AddField(
            model_name='basket',
            name='study',
            field=models.ForeignKey(blank=True, related_name='baskets', to='studies.Study', null=True, on_delete=models.CASCADE),
        ),
    ]

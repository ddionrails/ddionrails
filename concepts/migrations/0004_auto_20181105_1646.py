# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0003_auto_20181023_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concept',
            name='topic',
        ),
        migrations.AddField(
            model_name='concept',
            name='topics',
            field=models.ManyToManyField(related_name='concepts', to='concepts.Topic'),
        ),
    ]

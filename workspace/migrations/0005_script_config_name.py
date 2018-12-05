# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0004_script_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='config_name',
            field=models.CharField(default='soep-stata', max_length=255),
        ),
    ]

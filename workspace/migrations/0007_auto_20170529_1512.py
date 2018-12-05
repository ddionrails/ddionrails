# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0006_auto_20170313_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='study',
            field=models.ForeignKey(default=1, related_name='baskets', to='studies.Study', on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]

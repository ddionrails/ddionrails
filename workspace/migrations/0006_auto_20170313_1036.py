# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0005_script_config_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='script',
            old_name='config_name',
            new_name='generator_name',
        ),
    ]

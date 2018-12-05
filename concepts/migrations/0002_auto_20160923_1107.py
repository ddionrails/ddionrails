# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.validators


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='name',
            field=models.CharField(max_length=255, validators=[ddionrails.validators.validate_lowercase]),
        ),
        migrations.AlterUniqueTogether(
            name='period',
            unique_together=set([('study', 'name')]),
        ),
    ]

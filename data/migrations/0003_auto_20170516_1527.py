# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_variable_description_long'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transformation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('origin', models.ForeignKey(related_name='target_variables', to='data.Variable', on_delete=models.CASCADE)),
                ('target', models.ForeignKey(related_name='origin_variables', to='data.Variable', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='transformation',
            unique_together=set([('origin', 'target')]),
        ),
    ]

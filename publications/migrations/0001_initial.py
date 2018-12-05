# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.mixins
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('study', models.ForeignKey(related_name='publications', null=True, blank=True, to='studies.Study', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([('study', 'name')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.mixins
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('repo', models.CharField(blank=True, max_length=255)),
                ('webhook_token', models.CharField(blank=True, max_length=255)),
                ('current_commit', models.CharField(blank=True, max_length=255)),
                ('files_url', models.CharField(blank=True, max_length=255)),
                ('organization', models.ForeignKey(related_name='studies', null=True, blank=True, to='studies.Organization', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
    ]

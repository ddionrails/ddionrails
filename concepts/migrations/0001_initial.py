# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.mixins
import ddionrails.validators


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisUnit',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            bases=(models.Model, ddionrails.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            bases=(models.Model, ddionrails.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name='ConceptualDataset',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            bases=(models.Model, ddionrails.mixins.ModelMixin),
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], unique=True, max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('definition', models.CharField(blank=True, max_length=255)),
                ('study', models.ForeignKey(to='studies.Study', related_name='periods', on_delete=models.CASCADE)),
            ],
            bases=(models.Model, ddionrails.mixins.ModelMixin),
        ),
    ]

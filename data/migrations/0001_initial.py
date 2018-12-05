# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.validators
import ddionrails.mixins
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0001_initial'),
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('analysis_unit', models.ForeignKey(related_name='datasets', null=True, blank=True, to='concepts.AnalysisUnit', on_delete=models.CASCADE)),
                ('conceptual_dataset', models.ForeignKey(related_name='datasets', null=True, blank=True, to='concepts.ConceptualDataset', on_delete=models.CASCADE)),
                ('period', models.ForeignKey(related_name='datasets', null=True, blank=True, to='concepts.Period', on_delete=models.CASCADE)),
                ('study', models.ForeignKey(related_name='datasets', null=True, blank=True, to='studies.Study', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=False)),
                ('study', models.ForeignKey(related_name='releases', null=True, blank=True, to='studies.Study', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('sort_id', models.IntegerField(blank=True, null=True)),
                ('concept', models.ForeignKey(related_name='variables', null=True, blank=True, to='concepts.Concept', on_delete=models.CASCADE)),
                ('dataset', models.ForeignKey(related_name='variables', null=True, blank=True, to='data.Dataset', on_delete=models.CASCADE)),
                ('period', models.ForeignKey(related_name='variables', null=True, blank=True, to='concepts.Period', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together=set([('name', 'dataset')]),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('study', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together=set([('study', 'name')]),
        ),
    ]

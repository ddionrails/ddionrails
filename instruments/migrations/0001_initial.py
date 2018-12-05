# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.validators
import ddionrails.mixins
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
        ('concepts', '0001_initial'),
        ('studies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('analysis_unit', models.ForeignKey(related_name='instruments', null=True, blank=True, to='concepts.AnalysisUnit', on_delete=models.CASCADE)),
                ('period', models.ForeignKey(related_name='instruments', null=True, blank=True, to='concepts.Period', on_delete=models.CASCADE)),
                ('study', models.ForeignKey(related_name='instruments', null=True, blank=True, to='studies.Study', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('sort_id', models.IntegerField(blank=True, null=True)),
                ('instrument', models.ForeignKey(related_name='questions', null=True, blank=True, to='instruments.Instrument', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='QuestionVariable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('question', models.ForeignKey(to='instruments.Question', related_name='questions_variables', on_delete=models.CASCADE)),
                ('variable', models.ForeignKey(to='data.Variable', related_name='questions_variables', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='questionvariable',
            unique_together=set([('question', 'variable')]),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('instrument', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='instrument',
            unique_together=set([('study', 'name')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0002_auto_20160923_1107'),
        ('instruments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConceptQuestion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('concept', models.ForeignKey(related_name='concepts_questions', to='concepts.Concept', on_delete=models.CASCADE)),
                ('question', models.ForeignKey(related_name='concepts_questions', to='instruments.Question', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='conceptquestion',
            unique_together=set([('question', 'concept')]),
        ),
    ]

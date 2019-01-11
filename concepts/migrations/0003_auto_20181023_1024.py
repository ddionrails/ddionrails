# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.mixins
import ddionrails.validators
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0004_auto_20180926_1719'),
        ('concepts', '0002_auto_20160923_1107'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=255, validators=[ddionrails.validators.validate_lowercase])),
                ('label', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('parent', models.ForeignKey(to='concepts.Topic', null=True, related_name='children', blank=True, on_delete=models.CASCADE)),
                ('study', models.ForeignKey(to='studies.Study', on_delete=models.CASCADE)),
            ],
            bases=(models.Model, ddionrails.mixins.ModelMixin, elastic.mixins.ModelMixin),
        ),
        migrations.AddField(
            model_name='concept',
            name='topic',
            field=models.ForeignKey(to='concepts.Topic', null=True, blank=True, on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together=set([('study', 'name')]),
        ),
    ]

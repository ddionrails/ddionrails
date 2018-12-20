# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ddionrails.validators
from django.conf import settings
import elastic.mixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(validators=[ddionrails.validators.validate_lowercase], max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('security_token', models.CharField(blank=True, max_length=255)),
                # ('release', models.ForeignKey(related_name='baskets', null=True, blank=True, to='data.Release', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='baskets', on_delete=models.CASCADE)),
            ],
            bases=(elastic.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BasketVariable',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('basket', models.ForeignKey(to='workspace.Basket', related_name='baskets_variables', on_delete=models.CASCADE)),
                ('variable', models.ForeignKey(to='data.Variable', related_name='baskets_variables', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='basket',
            name='variables',
            field=models.ManyToManyField(through='workspace.BasketVariable', to='data.Variable'),
        ),
        migrations.AlterUniqueTogether(
            name='basketvariable',
            unique_together=set([('basket', 'variable')]),
        ),
        migrations.AlterUniqueTogether(
            name='basket',
            unique_together=set([('user', 'name')]),
        ),
    ]

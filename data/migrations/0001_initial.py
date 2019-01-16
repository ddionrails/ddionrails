# Generated by Django 2.1.5 on 2019-01-16 13:34

import ddionrails.mixins
import ddionrails.validators
from django.db import migrations, models
import django.db.models.deletion
import elastic.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('studies', '0001_initial'),
        ('concepts', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, validators=[ddionrails.validators.validate_lowercase])),
                ('label', models.CharField(blank=True, max_length=255)),
                ('label_de', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True)),
                ('boost', models.FloatField(blank=True, null=True)),
                ('analysis_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='concepts.AnalysisUnit')),
                ('conceptual_dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='concepts.ConceptualDataset')),
                ('period', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='concepts.Period')),
                ('study', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='studies.Study')),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Transformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, validators=[ddionrails.validators.validate_lowercase])),
                ('label', models.CharField(blank=True, max_length=255)),
                ('label_de', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True)),
                ('description_long', models.TextField(blank=True)),
                ('sort_id', models.IntegerField(blank=True, null=True)),
                ('image_url', models.TextField(blank=True)),
                ('concept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='concepts.Concept')),
                ('dataset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='data.Dataset')),
                ('period', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='concepts.Period')),
            ],
            bases=(elastic.mixins.ModelMixin, ddionrails.mixins.ModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='transformation',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_variables', to='data.Variable'),
        ),
        migrations.AddField(
            model_name='transformation',
            name='target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_variables', to='data.Variable'),
        ),
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together={('name', 'dataset')},
        ),
        migrations.AlterUniqueTogether(
            name='transformation',
            unique_together={('origin', 'target')},
        ),
        migrations.AlterUniqueTogether(
            name='dataset',
            unique_together={('study', 'name')},
        ),
    ]

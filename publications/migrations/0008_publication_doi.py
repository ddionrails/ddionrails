# Generated by Django 2.1.5 on 2019-02-26 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0007_auto_20190110_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='doi',
            field=models.TextField(blank=True),
        ),
    ]

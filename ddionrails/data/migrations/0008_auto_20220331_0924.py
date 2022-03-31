# Generated by Django 3.2.12 on 2022-03-31 09:24
# pylint: disable-all

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0007_variable_statistics_flag"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="variable",
            name="image",
        ),
        migrations.RemoveField(
            model_name="variable",
            name="image_de",
        ),
        migrations.AddField(
            model_name="variable",
            name="images",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]

# Generated by Django 2.2.7 on 2019-11-28 09:09
# pylint: disable-all

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("data", "0002_auto_20191127_0829")]

    operations = [
        migrations.AlterField(
            model_name="variable",
            name="dataset",
            field=models.ForeignKey(
                blank=True,
                help_text="Foreign key to data.Dataset",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variables",
                to="data.Dataset",
            ),
        )
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("concepts", "0002_auto_20160923_1107"), ("publications", "0001_initial")]

    operations = [
        migrations.RenameField(model_name="publication", old_name="description", new_name="abstract"),
        migrations.RemoveField(model_name="publication", name="label"),
        migrations.AddField(model_name="publication", name="author", field=models.TextField(blank=True)),
        migrations.AddField(model_name="publication", name="cite", field=models.TextField(blank=True)),
        migrations.AddField(model_name="publication", name="date", field=models.TextField(blank=True)),
        migrations.AddField(
            model_name="publication",
            name="period",
            field=models.ForeignKey(to="concepts.Period", null=True, blank=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="publication", name="sub_type", field=models.CharField(max_length=255, blank=True)
        ),
        migrations.AddField(model_name="publication", name="title", field=models.TextField(blank=True)),
        migrations.AddField(model_name="publication", name="url", field=models.TextField(blank=True)),
    ]

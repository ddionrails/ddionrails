# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("studies", "0004_auto_20180926_1719"), ("publications", "0002_attachment")]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="context_study",
            field=models.ForeignKey(
                related_name="related_attachments", default=1, to="studies.Study", on_delete=models.CASCADE
            ),
            preserve_default=False,
        )
    ]

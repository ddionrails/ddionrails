from django.db import models

from ddionrails.studies.models import Study


class ScriptMetadata(models.Model):

    study = models.OneToOneField(
        Study, primary_key=True, unique=True, on_delete=models.CASCADE
    )
    metadata = models.JSONField(null=False, blank=False, default={})

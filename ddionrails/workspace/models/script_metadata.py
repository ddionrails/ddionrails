from django.db import models

from ddionrails.studies.models import Study


class ScriptMetadata(models.Model):

    data = models.JSONField(default={}, blank=False, null=False)
    study = models.OneToOneField(
        Study, on_delete=models.CASCADE, primary_key=True, unique=True
    )

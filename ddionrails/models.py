import os

from django.conf import settings
from django.db import models


class System(models.Model):
    name = settings.SYSTEM_NAME
    current_commit = models.CharField(max_length=255, blank=True)

    def repo_url(self):
        return settings.SYSTEM_REPO_URL

    def import_path(self):
        path = os.path.join(
            settings.IMPORT_REPO_PATH, self.name, settings.IMPORT_SUB_DIRECTORY
        )
        return path

    @classmethod
    def get(cls):
        if cls.objects.count() == 0:
            s = System()
            s.save()
        else:
            s = System.objects.first()
        return s

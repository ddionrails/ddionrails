# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.base app """

from __future__ import annotations

import pathlib

from django.conf import settings
from django.db import models


class System(models.Model):
    """ Stores a single system instance """

    name = settings.SYSTEM_NAME
    current_commit = models.CharField(max_length=255, blank=True)

    @staticmethod
    def repo_url() -> str:
        """ Returns the system's repo url from the settings """
        return settings.SYSTEM_REPO_URL

    def import_path(self) -> pathlib.Path:
        """ Returns the system's import path """
        return pathlib.Path(settings.IMPORT_REPO_PATH).joinpath(
            self.name, settings.IMPORT_SUB_DIRECTORY
        )

    @classmethod
    def get(cls) -> System:
        """ Returns a single system instance """
        if cls.objects.count() == 0:
            system = System()
            system.save()
        else:
            system = System.objects.first()
        return system

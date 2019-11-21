# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.base app """

from __future__ import annotations

from django.conf import settings
from django.db import models

from .mixins import ImportPathMixin


class System(ImportPathMixin, models.Model):
    """ Stores a single system instance """

    name = settings.SYSTEM_NAME
    current_commit = models.CharField(max_length=255, blank=True)

    @staticmethod
    def repo_url() -> str:
        """ Returns the system's repo url from the settings """
        return settings.SYSTEM_REPO_URL

    @classmethod
    def get(cls) -> System:
        """ Returns a single system instance """
        if (system := System.objects.first()) is None:
            system = System()
            system.save()
        return system

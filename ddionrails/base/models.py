# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.base app """

from __future__ import annotations

from django.conf import settings
from django.db import models

from .mixins import ImportPathMixin


class Singleton(models.Model):
    """Base Class for models with just one entry."""

    class Meta:
        abstract = True

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Save instance and delete possible other table entries."""
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
        self.__class__.objects.exclude(id=self.id).delete()  # type:ignore


class System(ImportPathMixin, Singleton):
    """Information about the git repository containing initialization information."""

    class Meta:
        abstract = False

    name = settings.SYSTEM_NAME
    current_commit = models.CharField(max_length=255, blank=True)

    @staticmethod
    def repo_url() -> str:
        """ Returns the system's repo url from the settings """
        return settings.SYSTEM_REPO_URL

    @classmethod
    def get(cls) -> System:
        """ Returns a single system instance """
        fallback_system: System
        if (system := System.objects.first()) is None:
            fallback_system = System()
            fallback_system.save()
        return system or fallback_system


class News(Singleton):
    """A single page update text with its creation date attached."""

    class Meta:
        abstract = False
        verbose_name_plural = "news"

    date = models.DateTimeField(auto_now=True)
    content = models.TextField()

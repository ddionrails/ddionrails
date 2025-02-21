# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.base app """

from __future__ import annotations

from django.conf import settings
from django.db import models


class Singleton(models.Model):
    """Base Class for models with just one entry."""

    id = models.AutoField(primary_key=True)

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

class News(Singleton):
    """A single page update text with its creation date attached."""

    class Meta:
        abstract = False
        verbose_name_plural = "news"

    date = models.DateTimeField(auto_now=True)
    content = models.TextField(default="")
    content_de = models.TextField(default="")

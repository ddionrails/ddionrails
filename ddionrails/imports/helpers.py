# -*- coding: utf-8 -*-

""" Helper functions for ddionrails.imports app """

import csv
import os
import uuid
from functools import lru_cache

from django.conf import settings


def read_csv(filename, path=None):
    """
    Generic function to import a CSV file and return it as a dict.
    """
    if path:
        filename = os.path.join(path, filename)
    with open(filename, "r", encoding="utf8") as file:
        content = list(csv.DictReader(file))
    return content


def hash_with_base_uuid(name: str, cache: bool = True) -> uuid.UUID:
    """Compute the model instance's UUID from its name and the base UUID"""
    if cache:
        return _hash_with_base_uuid(name)
    return uuid.uuid5(settings.BASE_UUID, name)


@lru_cache(maxsize=1000)
def _hash_with_base_uuid(name: str) -> uuid.UUID:
    """Computes results for hash_with_base_uuid with an lru cache enabled."""
    return uuid.uuid5(settings.BASE_UUID, name)


def hash_with_namespace_uuid(
    namespace: uuid.UUID, name: str, cache: bool = True
) -> uuid.UUID:
    """Compute the model instance's UUID inside a namespace.

    A namespace, in this instance, is defined by the UUID of a related model instance.
    """
    if cache:
        return _hash_with_namespace_uuid(namespace, name)
    return uuid.uuid5(namespace, name)


@lru_cache(maxsize=1000)
def _hash_with_namespace_uuid(namespace: uuid.UUID, name: str) -> uuid.UUID:
    """Computes results for hash_with_namespace_uuid with an lru cache enabled."""
    return uuid.uuid5(namespace, name)

# -*- coding: utf-8 -*-

""" Helper functions for ddionrails.base app """

import uuid
from functools import lru_cache

from django.conf import settings


def hash_with_base_uuid(name: str, cache: bool = True):
    """ Compute the model instance's UUID from its name and the base UUID """
    if cache:
        return _hash_with_base_uuid(name)
    else:
        return uuid.uuid5(settings.BASE_UUID, name)


@lru_cache(maxsize=1000)
def _hash_with_base_uuid(name: str):
    """ Compute the model instance's UUID from its name and the base UUID, caching results """
    return uuid.uuid5(settings.BASE_UUID, name)


def hash_with_namespace_uuid(namespace: uuid.UUID, name: str, cache: bool = True):
    """ Compute the model instance's UUID from its name and a related object's UUID """
    if cache:
        return _hash_with_namespace_uuid(namespace, name)
    else:
        return uuid.uuid5(namespace, name)


@lru_cache(maxsize=1000)
def _hash_with_namespace_uuid(namespace: uuid.UUID, name: str):
    """ Compute the model instance's UUID from its name and a related object's UUID, caching results """
    return uuid.uuid5(namespace, name)

# -*- coding: utf-8 -*-

""" Helper functions for ddionrails.imports app """

import csv
import os
import uuid
from functools import lru_cache
from io import BytesIO
from typing import BinaryIO, List, Optional, Tuple, Union

import requests
from django.conf import settings
from filer.fields.folder import Folder
from filer.models import Image
from requests.exceptions import RequestException


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
    """ Compute the model instance's UUID from its name and the base UUID """
    if cache:
        return _hash_with_base_uuid(name)
    return uuid.uuid5(settings.BASE_UUID, name)


@lru_cache(maxsize=1000)
def _hash_with_base_uuid(name: str) -> uuid.UUID:
    """ Computes results for hash_with_base_uuid with an lru cache enabled. """
    return uuid.uuid5(settings.BASE_UUID, name)


def hash_with_namespace_uuid(
    namespace: uuid.UUID, name: str, cache: bool = True
) -> Optional[uuid.UUID]:
    """ Compute the model instance's UUID inside a namespace.

    A namespace, in this instance, is defined by teh UUID of a related model instance.
    """
    if not name:
        return None
    if cache:
        return _hash_with_namespace_uuid(namespace, name)
    return uuid.uuid5(namespace, name)


@lru_cache(maxsize=1000)
def _hash_with_namespace_uuid(namespace: uuid.UUID, name: str) -> uuid.UUID:
    """ Computes results for hash_with_namespace_uuid with an lru cache enabled. """
    return uuid.uuid5(namespace, name)


def download_image(url: str) -> Optional[BytesIO]:
    """ Load data from a web address into a BytesIO object.

    Args:
        url: Web address in a form, that is retrievable by requests.get()

    Returns:
        The ressource located at the address.
    """
    max_size = 200000
    _data = b""
    try:
        response = requests.get(url, timeout=10, stream=True)
    except RequestException:
        return None
    else:
        if response.status_code != 200:
            return None
        for chunk in response.iter_content(chunk_size=50000):
            _data = _data + chunk
            if len(_data) > max_size:
                response.close()
                return None
        response.close()
        _output = BytesIO(_data)
    return _output


def store_image(
    file: BinaryIO, name: str, path: Union[List, str]
) -> Tuple[Image, uuid.UUID]:
    """ Store an image for this QuestionImage.

    Args
        file: The image file to be stored.
        name: The name associated with the image.
        path: The folder path where the image should be stored.

    Returns:
        The Image model object in the first place of the tuple.
        The objects database key/id.
    """
    file.seek(0)

    _folder = _create_folder_structure(path)
    _filer_image = Image(folder=_folder, name=name)
    _filer_image.folder = _folder
    _filer_image.file.save(name=name, content=file)
    _filer_image.save()
    _image_id = _filer_image.pk
    return (_filer_image, _image_id)


def _create_folder_structure(path: Union[List, str]) -> Folder:
    """Create folders and subfolders needed for the image storage.

    Args:
        path: Will be split into a list at the / characters if it is a string.
              It will not be altered if a list ist passed.
              path represents a folder structure. An element is in a
              parent(folder)-child(folder)-relation with the next element in the list.
    Returns:
        The leaf of the structure, i.e. the folder without a child.
    """
    if isinstance(path, str):
        _path = path.split("/")
    else:
        _path = path
    # Filter out the possible "" because a folder needs a name
    _path = [folder for folder in _path if folder]
    _parent, _ = Folder.objects.get_or_create(name=_path[0])
    for folder in _path[1:]:
        _parent, _ = Folder.objects.get_or_create(name=folder, parent=_parent)
    return _parent

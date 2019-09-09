# -*- coding: utf-8 -*-

""" Helper functions for ddionrails.imports app """

import csv
import os
import uuid
from functools import lru_cache
from io import BytesIO
from typing import BinaryIO, Dict, List, Optional, Tuple, Union

import requests
import tablib
from django.conf import settings
from filer.fields.folder import Folder
from filer.models import Image


def read_csv(filename, path=None):
    """
    Generic function to import a CSV file and return it as a dict.
    """
    if path:
        filename = os.path.join(path, filename)
    with open(filename, "r") as file:
        content = [row for row in csv.DictReader(file)]
    return content


def hash_with_base_uuid(name: str, cache: bool = True) -> Optional[uuid.UUID]:
    """ Compute the model instance's UUID from its name and the base UUID """
    if not name:
        return None
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


def rename_dataset_headers(dataset: tablib.Dataset, rename_mapping: Dict) -> None:
    """ Rename the headers of a tablib.Dataset.

    Args:
        dataset: The Dataset object to be altered
        rename_mapping: With keys representing old header names and values
                        representing the names they will be changed to.
    """

    for old_name, new_name in rename_mapping.items():
        if old_name in dataset.headers:
            dataset.headers[dataset.headers.index(old_name)] = new_name


def add_id_to_dataset(
    dataset: tablib.Dataset, column_name: str, namespace_column: str = None
) -> None:
    """ Add an ID column into the given dataset

        Computes an UUID using the contents of the given dataset's column
        (i.e. column name)
        and optionally the contents of the namespace_column
    """

    # variable resource can get input from csv or json file:
    # concept might be there or not.
    if column_name not in dataset.headers:
        return

    id_list = []
    id_column_name = f"{column_name}_id"

    for index, name in enumerate(dataset[column_name]):
        if name:
            namespace = dataset[namespace_column][index]
            computed_id = hash_with_namespace_uuid(namespace, name, cache=True)
        # if column cell is empty do not compute id -> foreign key is None / Null
        else:
            computed_id = None
        id_list.append(computed_id)

    # add id column to dataset
    dataset.append_col(id_list, header=id_column_name)


def add_image_to_dataset(dataset: tablib.Dataset):
    """ Creates the datastructure for the image import.

    Replaces the content of the passed dataset.
    This new dataset, contains a row for every image with a calculated UUID,
    language information and label text linked to the associated language.

    Args:
        dataset: Contains a row with metadata for
                 the english and the german Image of a question
    """
    new_dataset = tablib.Dataset()
    new_dataset.headers = (
        "question_id",
        "question_image_id",
        "image",
        "label",
        "language",
    )
    _headers = dataset.headers
    for row in dataset:
        if row[_headers.index("url")]:
            image = download_image(row[_headers.index("url")])
            stored_image, _ = store_image(
                image,
                path=[
                    row[_headers.index("study")],
                    row[_headers.index("instrument")],
                    row[_headers.index("question")],
                ],
                name=row[_headers.index("label")] + "_en",
            )
            new_dataset.append(
                (
                    row[_headers.index("question_id")],
                    hash_with_namespace_uuid(
                        row[_headers.index("question_id")],
                        row[_headers.index("label")] + "en",
                    ),
                    stored_image,
                    row[_headers.index("label")],
                    "en",
                )
            )
        if row[_headers.index("url_de")]:
            image = download_image(row[_headers.index("url_de")])
            stored_image, _ = store_image(
                image,
                path=[
                    row[_headers.index("study")],
                    row[_headers.index("instrument")],
                    row[_headers.index("question")],
                ],
                name=row[_headers.index("label_de")] + "_de",
            )
            new_dataset.append(
                (
                    row[_headers.index("question_id")],
                    hash_with_namespace_uuid(
                        row[_headers.index("question_id")],
                        row[_headers.index("label_de")] + "de",
                    ),
                    stored_image,
                    row[_headers.index("label_de")],
                    "de",
                )
            )

    dataset.wipe()
    dataset.headers = new_dataset.headers
    for row in new_dataset:
        dataset.append(row)


def add_base_id_to_dataset(dataset: tablib.Dataset, column_name: str) -> None:
    """ Add ID column UUIDs created with the systems base UUID

    This is only used to get the UUIDs from a study column.
    We do not test if all rows inside the column are filled.
    A row without a value for study shows that the data is faulty and should
    fail to be imported.
    """
    id_column = []
    id_column_name = f"{column_name}_id"
    for name in dataset[column_name]:
        id_column.append(hash_with_base_uuid(name))

    dataset.append_col(id_column, header=id_column_name)


def add_concept_id_to_dataset(dataset: tablib.Dataset, column_name: str) -> None:
    """ Add Concept ID column into the given dataset.

        Like add_id_to_dataset but concepts are hashed with the base UUID.
        Since Studies are also hashed with the base UUID, concepts need
        to be differentiate if we want to guarantee unique UUIDs.
        This is done by concatenating their name with the string "concept:".
    """
    id_column = []
    id_column_name = f"{column_name}_id"
    _prefix = "concept:{}"
    for name in dataset[column_name]:
        if name:
            id_column.append(hash_with_base_uuid(_prefix.format(name)))
        else:
            id_column.append(None)

    dataset.append_col(id_column, header=id_column_name)


def download_image(url: str) -> BytesIO:
    """ Load data from a web address into a BytesIO object.

    Args:
        url: Web address in a form, that is retrievable by requests.get()

    Returns:
        The ressource located at the address.
    """
    _data = requests.get(url).content
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

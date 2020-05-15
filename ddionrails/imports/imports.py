# -*- coding: utf-8 -*-

""" Importer base classes for ddionrails project """

import logging
import os
from pathlib import Path
from typing import Iterable, Union

import frontmatter
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.forms import Form

from ddionrails.studies.models import Study

from .helpers import read_csv

logging.config.fileConfig("logging.conf")  # type: ignore
LOGGER = logging.getLogger(__name__)


class Import:
    """
    **Abstract class.**

    To use it, implement the ``execute_import()`` method.
    """

    content: Union[None, str, Iterable]

    def __init__(self, filename: Union[Path, str], study: Study = None, system=None):
        self.study = study
        self.system = system
        self.filename = filename
        self.basename = os.path.basename(self.filename)
        self.name = os.path.splitext(self.basename)[0]
        self.content = None

    class DOR:  # pylint: disable=missing-docstring,too-few-public-methods
        form = Form

    def execute_import(self):
        raise NotImplementedError

    @classmethod
    @transaction.atomic
    def run_import(cls, filename, study=None):
        importer = cls(filename, study)
        importer.read_file()
        importer.execute_import()

    def read_file(self):
        with open(self.file_path(), "r") as infile:
            self.content = infile.read()

    def import_path(self):
        if self.study:
            return self.study.import_path()
        return self.system.import_path()

    def file_path(self):
        return self.filename


class JekyllImport(Import):
    """
    This import is based on the design for `Jekyll <http://jekyllrb.com>`__
    pages, which combine a YAML front matter with Markdown content.

    The front matter is seperated with three dashes (``---``).

    Example::

        ---
        title: test
        abstract: Some test document
        ---

        The *actual* content is using
        [Markdown](http://daringfireball.net/projects/markdown/).
    """

    def __init__(self, filename, study=None, system=None):
        super().__init__(filename, study, system)
        self.data = None

    def read_file(self):
        with open(self.file_path(), "r") as infile:
            jekyll_content = frontmatter.load(infile)
        self.content = jekyll_content.content
        self.data = jekyll_content.metadata

    def execute_import(self):
        raise NotImplementedError


class CSVImport(Import):
    """
    **Abstract class.**

    To use it, implement the ``process_element()`` method.
    """

    def read_file(self):
        self.content: Iterable = read_csv(self.file_path())

    def execute_import(self):
        for element in self.content:
            self.import_element(element)

    def import_element(self, element):
        form = self.DOR.form
        element = self.process_element(element)
        try:
            model = self.DOR.form.Meta.model  # type: ignore
            fields = model.DOR.id_fields
            definition = {
                key: value for key, value in form(element).data.items() if key in fields
            }
            obj = model.objects.get(**definition)
        # afuetterer: the object might not be found with "model.objects.get()"
        # or the model might not have "model.DOR.id_fields"
        except (AttributeError, ObjectDoesNotExist):
            obj = None
        # mypy django-stubs seem to have a problem with forms.
        form = self.DOR.form(element, instance=obj)  # type: ignore
        form.full_clean()  # type: ignore
        if form.is_valid():  # type: ignore
            new_object = form.save()  # type: ignore
            print(".", end="")
            return new_object
        LOGGER.error("Import error in %s", str(self.__class__))
        LOGGER.error(form.data)
        LOGGER.error(form.errors.as_data())  # type: ignore
        return None

    def process_element(self, element):
        return element

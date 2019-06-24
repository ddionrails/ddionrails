# -*- coding: utf-8 -*-

""" Importer base classes for ddionrails project """

import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.forms import Form

from .helpers import read_csv

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


class Import:
    """
    **Abstract class.**

    To use it, implement the ``execute_import()`` method.
    """

    def __init__(self, filename, study=None, system=None):
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


class CSVImport(Import):
    """
    **Abstract class.**

    To use it, implement the ``process_element()`` method.
    """

    def read_file(self):
        self.content = read_csv(self.file_path())

    def execute_import(self):
        for element in self.content:
            self.import_element(element)

    def import_element(self, element):
        form = self.DOR.form
        element = self.process_element(element)
        try:
            model = self.DOR.form.Meta.model
            fields = model.DOR.id_fields
            definition = {
                key: value for key, value in form(element).data.items() if key in fields
            }
            obj = model.objects.get(**definition)
        # afuetterer: the object might not be found with "model.objects.get()"
        # or the model might not have "model.DOR.id_fields"
        except (AttributeError, ObjectDoesNotExist):
            obj = None
        form = self.DOR.form(element, instance=obj)
        form.full_clean()
        if form.is_valid():
            new_object = form.save()
            print(".", end="")
            return new_object
        LOGGER.error("Import error in %s", str(self.__class__))
        LOGGER.error(form.data)
        LOGGER.error(form.errors.as_data())
        return None

    def process_element(self, element):
        return element

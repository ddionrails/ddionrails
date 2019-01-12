import logging
import os

import yaml
from django.db import transaction

from imports.helpers import read_csv

logger = logging.getLogger("imports")


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

    class DOR:
        form = None

    def execute_import(self):
        raise NotImplementedError

    @classmethod
    @transaction.atomic
    def run_import(cls, filename, study=None):
        importer = cls(filename, study)
        importer.read_file()
        importer.execute_import()

    def read_file(self):
        with open(self.file_path(), "r") as f:
            self.content = f.read()

    def import_path(self):
        if self.study:
            return self.study.import_path()
        else:
            return self.system.import_path()

    def file_path(self):
        return os.path.join(self.import_path(), self.filename)


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
        self.yaml_content = None

    def read_file(self):
        with open(self.file_path(), "r") as f:
            lines = f.read().splitlines()
            self.read_lines(lines)

    def read_lines(self, lines):
        yaml_lines = []
        line = lines.pop(0)
        if line == "---":
            while lines:
                line = lines.pop(0)
                if line in "---":
                    break
                yaml_lines.append(line)
        else:
            lines.insert(0, line)
        self.content = "\n".join(lines)
        self.yaml_content = "\n".join(yaml_lines)
        self.data = yaml.safe_load(self.yaml_content)

    def execute_import(self):
        print(self.data)
        print(self.content)


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
            x = model.objects.get(**definition)
        except:
            x = None
        form = self.DOR.form(element, instance=x)
        form.full_clean()
        if form.is_valid():
            new_object = form.save()
            print(".", end="")
            return new_object
        else:
            print("\nError:", self.__class__, "-", form.data)
            print(form.errors.as_data())
            logger.error("Import error in " + str(self.__class__))
            logger.error(form.data)
            logger.error(form.errors.as_data())
            return None

    def process_element(self, element):
        return element

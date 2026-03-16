# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

"""Test cases for importer classes in ddionrails.imports app"""


from unittest.mock import patch

from django.test import TestCase

from ddionrails.imports.imports import CSVImport, Import
from tests.model_factories import StudyFactory


class TestImport(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.study = StudyFactory()
        return super().setUpClass()

    def test_run_import_method(self):
        """Need a child of Import, because execute_import is not implemented"""

        class SampleImport(Import):
            def execute_import(self):
                return True

        with patch.object(SampleImport, "execute_import") as mocked_execute_import:
            with patch.object(SampleImport, "read_file") as mocked_read_file:
                SampleImport.run_import(filename="DUMMY.csv")
                mocked_execute_import.assert_called_once()
                mocked_read_file.assert_called_once()

    def test_read_file_method(self):
        filename = "DUMMY.csv"
        importer = Import(filename, study=self.study)
        with patch.object(Import, "file_path") as mocked_file_path:
            mocked_file_path.return_value = filename
            with patch("builtins.open") as mocked_open:
                importer.read_file()
                mocked_file_path.assert_called_once()
                mocked_open.assert_called_once_with(filename, "r", encoding="utf8")


class TestCSVImport(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.study = StudyFactory()
        cls.csv_importer = CSVImport("DUMMY.csv", cls.study)
        return super().setUpClass()

    def test_read_file_method(self):
        with patch("ddionrails.imports.imports.read_csv") as mocked_read_csv:
            with patch.object(self.csv_importer, "file_path") as mocked_file_path:
                self.csv_importer.read_file()
                mocked_read_csv.assert_called_once()
                mocked_file_path.assert_called_once()

    def test_execute_import_method(self):
        with patch.object(self.csv_importer, "import_element") as mocked_import_element:
            self.csv_importer.content = ["element"]
            self.csv_importer.execute_import()
            mocked_import_element.assert_called_once_with("element")

    def test_process_element_method(self):
        element = "element"
        response = self.csv_importer.process_element(element)
        assert response == element

# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,invalid-name

""" Test cases for importer classes in ddionrails.imports app """

import pathlib

import pytest
from django.db import models
from django.forms import ModelForm

from ddionrails.imports.imports import CSVImport, Import, JekyllImport

pytestmark = [pytest.mark.imports]


@pytest.fixture
def filename():
    return "DUMMY.csv"


@pytest.fixture
def csv_importer(study, filename):
    """ A csv importer """
    return CSVImport(filename, study=study)


@pytest.fixture
def jekyll_importer(study, filename):
    """ A jekyll importer """
    return JekyllImport(filename, study=study)


class TestImport:
    @pytest.mark.django_db
    def test_run_import_method(self, mocker):
        """ Need a child of Import, because execute_import is not implemented """

        class SampleImport(Import):
            def execute_import(self):
                return True

        mocked_execute_import = mocker.patch.object(SampleImport, "execute_import")
        mocked_read_file = mocker.patch.object(SampleImport, "read_file")
        SampleImport.run_import(filename="DUMMY.csv")
        mocked_execute_import.assert_called_once()
        mocked_read_file.assert_called_once()

    def test_read_file_method(self, study, mocker):
        filename = "DUMMY.csv"
        importer = Import(filename, study=study)
        mocked_file_path = mocker.patch.object(Import, "file_path")
        mocked_file_path.return_value = filename
        mocked_open = mocker.patch("builtins.open")
        importer.read_file()
        mocked_file_path.assert_called_once()
        mocked_open.assert_called_once_with(filename, "r")

    def test_import_path_method_with_study(self, study, settings):
        importer = Import(filename="DUMMY.csv", study=study)
        result = importer.import_path()
        path = pathlib.Path(settings.IMPORT_REPO_PATH).joinpath(
            study.name, settings.IMPORT_SUB_DIRECTORY
        )
        expected = str(path) + "/"
        assert expected == result

    def test_import_path_method_without_study(self, system, settings):
        importer = Import(filename="DUMMY.csv", system=system)
        result = importer.import_path()
        expected = pathlib.Path(settings.IMPORT_REPO_PATH).joinpath(
            system.name, settings.IMPORT_SUB_DIRECTORY
        )
        assert expected == result

    # def test_file_path_method(self, mocker):
    #     importer = Import(filename="DUMMY.csv")
    #     mocked_import_path = mocker.patch.object(Import, "import_path")
    #     mocked_import_path.return_value = "path"
    #     file_path = importer.file_path()
    #     assert file_path == "path/DUMMY.csv"


class TestCSVImport:
    def test_read_file_method(self, mocker, csv_importer):
        mocked_read_csv = mocker.patch("ddionrails.imports.imports.read_csv")
        mocked_file_path = mocker.patch.object(CSVImport, "file_path")
        csv_importer.read_file()
        mocked_read_csv.assert_called_once()
        mocked_file_path.assert_called_once()

    def test_execute_import_method(self, mocker, csv_importer):
        mocked_import_element = mocker.patch.object(CSVImport, "import_element")
        csv_importer.content = ["element"]
        csv_importer.execute_import()
        mocked_import_element.assert_called_once_with("element")

    @pytest.mark.skip
    def test_import_element_method(self, mocker, csv_importer):
        mocked_process_element = mocker.patch.object(CSVImport, "process_element")

        class SampleModel(models.Model):
            pass

        class SampleForm(ModelForm):
            class Meta:
                model = SampleModel

        class SampleImport(CSVImport):
            class DOR:
                form = SampleForm

        sample_importer = SampleImport("DUMMY.CSV")
        element = "element"
        sample_importer.import_element(element)

    def test_process_element_method(self, csv_importer):
        element = "element"
        respone = csv_importer.process_element(element)
        assert respone == element


@pytest.mark.skip
class TestJekyllImport:
    def test_read_file_method(self, mocker, jekyll_importer):
        mocked_read_lines = mocker.patch.object(JekyllImport, "read_lines")
        mocked_open = mocker.patch("builtins.open")
        jekyll_importer.read_file()
        mocked_read_lines.assert_called_once()
        mocked_open.assert_called_once()

    def test_read_lines_method(self, mocker, jekyll_importer):
        mocked_safe_load = mocker.patch("yaml.safe_load")
        lines = ["---", "name: some-study", "---", "# Some Study"]
        jekyll_importer.read_lines(lines)
        assert jekyll_importer.content == "# Some Study"
        assert jekyll_importer.yaml_content == "name: some-study"
        mocked_safe_load.assert_called_once()

    def test_read_lines_method_without_dashed_line(self, mocker, jekyll_importer):
        mocked_safe_load = mocker.patch("yaml.safe_load")
        lines = ["name: some-study"]
        jekyll_importer.read_lines(lines)
        assert jekyll_importer.content == "name: some-study"
        assert jekyll_importer.yaml_content == ""
        mocked_safe_load.assert_called_once()

    def test_read_lines_method_with_only_dashed_line(self, mocker, jekyll_importer):
        mocked_safe_load = mocker.patch("yaml.safe_load")
        lines = ["---"]
        jekyll_importer.read_lines(lines)
        assert jekyll_importer.content == ""
        assert jekyll_importer.yaml_content == ""
        mocked_safe_load.assert_called_once()

    def test_execute_import_method(self, jekyll_importer, capsys):
        jekyll_importer.data = "some-data"
        jekyll_importer.content = "some-content"
        jekyll_importer.execute_import()
        out = capsys.readouterr()[0]
        assert out == "\n".join(["some-data", "some-content", ""])

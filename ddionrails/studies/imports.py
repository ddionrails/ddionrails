from ddionrails.imports import imports

from .forms import StudyInitialForm


class StudyDescriptionImport(imports.JekyllImport):
    def execute_import(self):
        study = self.study
        study.description = self.content
        study.label = self.data["label"]
        study.config = self.data["config"]
        study.save()


class StudyImport(imports.CSVImport):
    class DOR:
        form = StudyInitialForm

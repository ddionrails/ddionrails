import json

from imports import imports

from .forms import StudyInitialForm


class StudyDescriptionImport(imports.JekyllImport):

    def execute_import(self):
        study = self.study
        study.description = self.content
        study.label = self.data["label"]
        study.config = json.dumps(self.data["config"])
        study.set_elastic(dict(
            name=study.name,
            label=study.label,
            description=study.description,
        ))
        study.save()


class StudyImport(imports.CSVImport):

    class DOR:
        form = StudyInitialForm

from imports import imports

from .forms import (
    AnalysisUnitForm,
    ConceptForm,
    ConceptualDatasetForm,
    PeriodForm,
)


class ConceptImport(imports.CSVImport):

    class DOR:
        form = ConceptForm


class AnalysisUnitImport(imports.CSVImport):

    class DOR:
        form = AnalysisUnitForm


class PeriodImport(imports.CSVImport):

    class DOR:
        form = PeriodForm

    def process_element(self, element):
        element["study"] = self.study.id
        return element


class ConceptualDatasetImport(imports.CSVImport):

    class DOR:
        form = ConceptualDatasetForm

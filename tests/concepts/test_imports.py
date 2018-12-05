import pytest

from concepts.imports import AnalysisUnitImport, ConceptImport, ConceptualDatasetImport, PeriodImport
from concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period

pytestmark = [pytest.mark.concepts, pytest.mark.imports]


@pytest.fixture
def filename():
    return "DUMMY.csv"


@pytest.fixture
def concept_importer(db, filename):
    """ A concept importer """
    return ConceptImport(filename)


@pytest.fixture
def analysis_unit_importer(db, filename):
    """ An analysis unit importer """
    return AnalysisUnitImport(filename)


@pytest.fixture
def conceptual_dataset_importer(db, filename):
    """ A conceptual dataset importer """
    return ConceptualDatasetImport(filename)


@pytest.fixture
def period_importer(db, filename, study):
    """ A period importer """
    return PeriodImport(filename, study)


class TestConceptImport:
    def test_import_with_valid_data(self, concept_importer, valid_concept_data):
        response = concept_importer.import_element(valid_concept_data)
        assert isinstance(response, Concept)
        assert response.name == valid_concept_data["concept_name"]

    def test_import_with_invalid_data(self, concept_importer, empty_data):
        response = concept_importer.import_element(empty_data)
        assert response is None


class TestAnalysisUnitImport:
    def test_import_with_valid_data(self, analysis_unit_importer, valid_analysis_unit_data):
        response = analysis_unit_importer.import_element(valid_analysis_unit_data)
        assert isinstance(response, AnalysisUnit)
        assert response.name == valid_analysis_unit_data["analysis_unit_name"]

    def test_import_with_invalid_data(self, analysis_unit_importer, empty_data):
        response = analysis_unit_importer.import_element(empty_data)
        assert response is None


class TestConceptualDatasetImport:
    def test_import_with_valid_data(self, conceptual_dataset_importer, valid_conceptual_dataset_data):
        response = conceptual_dataset_importer.import_element(valid_conceptual_dataset_data)
        assert isinstance(response, ConceptualDataset)
        assert response.name == valid_conceptual_dataset_data["conceptual_dataset_name"]

    def test_import_with_invalid_data(self, conceptual_dataset_importer, empty_data):
        response = conceptual_dataset_importer.import_element(empty_data)
        assert response is None


class TestPeriodImport:
    def test_import_with_valid_data(self, period_importer, valid_period_data):
        response = period_importer.import_element(valid_period_data)
        assert isinstance(response, Period)
        assert response.name == valid_period_data["period_name"]

    def test_import_with_invalid_data(self, period_importer, empty_data):
        response = period_importer.import_element(empty_data)
        assert response is None

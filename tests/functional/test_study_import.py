import json
import time
from pathlib import Path
from pprint import pprint

import pytest
from elasticsearch import Elasticsearch

from concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period
from data.models import Dataset, Transformation, Variable
from ddionrails.models import System
from instruments.models import Instrument, Question
from publications.models import Publication
from scripts import import_studies
from studies.models import Study

pytestmark = [pytest.mark.imports, pytest.mark.functional]


def count_lines_in_file(filename):
    """ This function assumes
        that the file is present

    """
    with open(filename) as f:
        num_lines = sum(1 for line in f)
    return num_lines - 1  # minus header


class TestStudyImport:
    def test_import_study(self, db, settings):
        """ Tests the functionality of the script
            'scripts.import'

            it is run by:
                'paver import_all_studies'
            or
                'python manage.py runscript scripts.import'

            This script should:
             - download the study files from github
             - should import the metadata to the database

            The test requires a running elasticsearch instance

        """
        assert System.objects.count() == 0
        assert Study.objects.count() == 0
        assert Concept.objects.count() == 0
        assert ConceptualDataset.objects.count() == 0
        assert Dataset.objects.count() == 0
        assert Variable.objects.count() == 0
        assert Period.objects.count() == 0
        assert Publication.objects.count() == 0
        assert Question.objects.count() == 0
        assert Transformation.objects.count() == 0
        assert Instrument.objects.count() == 0

        study = Study.objects.create(
            name="soep-test", repo="github.com/ddionrails/testsuite"
        )
        assert Study.objects.count() == 1

        settings.IMPORT_BRANCH = "data-only"
        import_studies.run()
        study_root = Path("static/repositories/soep-test")
        assert study_root.exists()
        metadata_root = study_root / "ddionrails"

        concepts_file = metadata_root / "concepts.csv"
        datasets_file = metadata_root / "datasets.csv"
        variables_file = metadata_root / "variables.csv"
        analysis_units_file = metadata_root / "analysis_units.csv"
        conceptual_datasets_file = metadata_root / "conceptual_datasets.csv"
        periods_file = metadata_root / "periods.csv"
        questions_file = metadata_root / "questions_variables.csv"
        topics_file = metadata_root / "topics.csv"
        transformations_file = metadata_root / "transformations.csv"
        publications_file_csv = metadata_root / "publications.csv"
        publications_file_bib = metadata_root / "bibtex.bib"
        study_description_file = metadata_root / "study.md"

        assert concepts_file.exists()
        assert datasets_file.exists()
        assert variables_file.exists()
        assert analysis_units_file.exists()
        assert conceptual_datasets_file.exists()
        assert periods_file.exists()
        assert publications_file_csv.exists()
        assert publications_file_bib.exists()
        assert questions_file.exists()
        assert topics_file.exists()
        assert transformations_file.exists()
        assert study_description_file.exists()

        num_concepts_in_csv = count_lines_in_file(concepts_file)
        assert (
            Concept.objects.count() == num_concepts_in_csv
        ), "the number of concepts in the database does not match the number in the file"

        num_datasets_in_csv = count_lines_in_file(datasets_file)
        assert (
            Dataset.objects.count() == num_datasets_in_csv
        ), "the number of datasets in the database does not match the number in the file"

        # TODO: Fails. 79 vs 73. More variables in json, than csv?
        # num_variables_in_csv = count_lines_in_file(variables_file)
        # assert Variable.objects.count() == num_variables_in_csv, \
        #     'the number of variables in the database does not match the number in the file'

        num_analysis_units_in_csv = count_lines_in_file(analysis_units_file)
        assert (
            AnalysisUnit.objects.count() == num_analysis_units_in_csv
        ), "the number of analysis units in the database does not match the number in the file"

        num_conceptual_datasets_in_csv = count_lines_in_file(conceptual_datasets_file)

        # TODO: 3 vs. 8
        # assert (
        #     ConceptualDataset.objects.count() == num_conceptual_datasets_in_csv
        # ), "the number of conceptual datasets in the database does not match the number in the file"

        num_periods_in_csv = count_lines_in_file(periods_file)
        assert (
            Period.objects.count() == num_periods_in_csv
        ), "the number of periods in the database does not match the number in the file"

        # # TODO: Bibtex or publications.csv ?
        # # num_publications_in_csv = count_lines_in_file(publications_file)
        # with open(publications_file_bib, "r") as f:
        #     bibtex = bibtexparser.loads(f.read())
        # num_publications_in_bib = len(bibtex.entries)
        # assert (
        #     Publication.objects.count() == num_publications_in_bib
        # ), "the number of publications in the database does not match the number in the file"

        num_questions_in_csv = count_lines_in_file(questions_file)
        assert (
            Question.objects.count() == num_questions_in_csv
        ), "the number of questions in the database does not match the number in the file"

        num_transformations_in_csv = count_lines_in_file(transformations_file)
        assert (
            Transformation.objects.count() == num_transformations_in_csv
        ), "the number of transformations in the database does not match the number in the file"

        study = Study.objects.first()
        with open(study_description_file, "r") as f:
            description_from_file = f.read()
        assert study.description in description_from_file

        instruments_dir = metadata_root / "instruments"
        num_instruments = len(list(instruments_dir.glob("*.json")))
        assert num_instruments == Instrument.objects.count()

        datasets_dir = metadata_root / "datasets"
        num_datasets_json = len(list(datasets_dir.glob("*.json")))
        assert num_datasets_json == Dataset.objects.count()

        num_variables_in_json_files = 0
        for dataset in datasets_dir.glob("*.json"):
            with open(dataset, "r") as f:
                d = json.loads(f.read())
            num_variables_in_json_files += len(d)

        # assert num_variables_in_json_files == num_variables_in_es

    # TODO:
    # csv:
    # - attachments


def _create_index():
    "Create the index from the elastic/mapping.json file."
    print()
    print("####")
    print("# 1. creating index...")
    print("####")
    mapping_file = "elastic/mapping.json"
    with open(mapping_file, "r") as f:
        mapping = json.loads(f.read())
    es = Elasticsearch()
    es.indices.create(index="testing", ignore=400, body=mapping)
    # wait for elastic search index to be created
    time.sleep(0.1)
    print(es.indices.get_aliases().keys())


def _delete_index():
    es = Elasticsearch()
    print()
    print("####")
    print("# 2. deleting index...")
    print("####")
    es.indices.delete(index="testing", ignore=[400, 404])
    time.sleep(0.1)
    print(es.indices.get_aliases().keys())


@pytest.fixture(scope="module")
def es_client():
    _delete_index()
    _create_index()
    es = Elasticsearch()
    yield es
    _delete_index()


def count_documents_in_es_by_doctype(es_client, index, doc_type):
    print(index)
    return es_client.count(index, doc_type).get("count")


# @pytest.mark.skip(reason="no way of currently testing this")
def test_elastic_search_indexing(es_client, db, settings):
    num_documents_in_es = es_client.count(settings.INDEX_NAME).get("count")
    print("es testing:", num_documents_in_es)
    print(settings.INDEX_NAME)
    num_documents_in_es = es_client.count(settings.INDEX_NAME).get("count")
    assert num_documents_in_es == 0

    study = Study.objects.create(name="soep-test", repo="github.com/ddionrails/testsuite")
    assert Study.objects.count() == 1
    import_studies.run()

    # wait for indexing to be finished
    time.sleep(1)

    num_documents_in_es = es_client.count(settings.INDEX_NAME).get("count")
    print("es testing:", num_documents_in_es)

    num_questions_in_es = count_documents_in_es_by_doctype(
        es_client, settings.INDEX_NAME, "question"
    )
    num_publications_in_es = count_documents_in_es_by_doctype(
        es_client, settings.INDEX_NAME, "publication"
    )
    num_concepts_in_es = count_documents_in_es_by_doctype(
        es_client, settings.INDEX_NAME, "concept"
    )
    num_variables_in_es = count_documents_in_es_by_doctype(
        es_client, settings.INDEX_NAME, "variable"
    )
    num_studies_in_es = count_documents_in_es_by_doctype(
        es_client, settings.INDEX_NAME, "study"
    )

    print(num_studies_in_es)
    print(num_questions_in_es)
    print(num_publications_in_es)
    print(num_concepts_in_es)
    print(num_variables_in_es)

    assert num_documents_in_es == sum(
        (
            num_studies_in_es,
            num_questions_in_es,
            num_publications_in_es,
            num_concepts_in_es,
            num_variables_in_es,
        )
    )

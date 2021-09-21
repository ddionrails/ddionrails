# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

import csv
import json
import unittest
from pathlib import Path

import pytest
from django.core.management import call_command

from ddionrails.concepts.documents import ConceptDocument
from ddionrails.concepts.models import (
    AnalysisUnit,
    Concept,
    ConceptualDataset,
    Period,
    Topic,
)
from ddionrails.data.documents import VariableDocument
from ddionrails.data.models import Dataset, Transformation, Variable
from ddionrails.imports.manager import StudyImportManager
from ddionrails.instruments.documents import QuestionDocument
from ddionrails.instruments.models import (
    ConceptQuestion,
    Instrument,
    Question,
    QuestionVariable,
)
from ddionrails.publications.documents import PublicationDocument
from ddionrails.publications.models import Attachment, Publication
from ddionrails.studies.models import Study, TopicList
from tests.data.factories import VariableFactory

TEST_CASE = unittest.TestCase()

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.filterwarnings("ignore::DeprecationWarning")
]


@pytest.fixture(name="study_import_manager")
def _study_import_manager(study, settings):
    settings.IMPORT_REPO_PATH = Path("tests/functional/test_data/")
    manager = StudyImportManager(study)
    return manager


@pytest.fixture(name="clean_search_index")
def _clean_search_index():
    yield
    call_command("search_index", "--delete", force=True)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_import_path", "clean_search_index")
class TestStudyImportManager:
    def test_import_study(self, study_import_manager):  # pylint: disable=unused-argument
        study_import_manager.import_single_entity("study")
        TEST_CASE.assertEqual(1, Study.objects.count())
        # refresh
        study = Study.objects.first()
        TEST_CASE.assertEqual("Some Study", study.label)
        TEST_CASE.assertEqual({"variables": {"label-table": True}}, study.config)

    def test_import_csv_topics(self, study_import_manager):
        TEST_CASE.assertEqual(0, Topic.objects.count())
        study_import_manager.import_single_entity("topics.csv")
        TEST_CASE.assertEqual(2, Topic.objects.count())
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        TEST_CASE.assertEqual("some-label", topic.label)
        TEST_CASE.assertEqual(parent_topic, topic.parent)
        TEST_CASE.assertEqual("some-other-label", parent_topic.label)

    def test_import_csv_topics_exception(self, study_import_manager):
        import_path: Path = study_import_manager.study.import_path()

        faulty_row = {
            "study": "some-nonexistent-study",
            "name": "some-topic",
            "label": "some-label",
            "label_de": "some-german-label",
            "description": "Some description",
            "description_de": "Eine Beschreibung",
            "parent": "some-other-topic",
        }
        with open(import_path.joinpath("topics.csv"), "a", encoding="utf8") as topic_file:
            writer = csv.DictWriter(topic_file, fieldnames=list(faulty_row.keys()))
            writer.writerow(faulty_row)

        with TEST_CASE.assertRaises(Study.DoesNotExist):
            study_import_manager.import_single_entity("topics.csv")

    def test_import_json_topics(
        self, study_import_manager
    ):  # pylint: disable=unused-argument
        TEST_CASE.assertEqual(1, Study.objects.count())
        TEST_CASE.assertEqual(0, Topic.objects.count())
        TEST_CASE.assertEqual(0, TopicList.objects.count())
        study_import_manager.import_single_entity("study")
        study_import_manager.import_single_entity("topics.json")
        TEST_CASE.assertEqual(1, Study.objects.count())
        TEST_CASE.assertEqual(1, TopicList.objects.count())
        study = Study.objects.first()
        topiclist = TopicList.objects.first()
        TEST_CASE.assertEqual(study, topiclist.study)
        english_topics = topiclist.topiclist[0]
        TEST_CASE.assertEqual("en", english_topics["language"])
        german_topics = topiclist.topiclist[1]
        TEST_CASE.assertEqual("de", german_topics["language"])

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_concepts(self, study, topic):
        TEST_CASE.assertEqual(0, Concept.objects.count())
        with TEST_CASE.assertRaises(SystemExit) as _exit:
            call_command("update", study.name, "concepts", "-l")
            TEST_CASE.assertEqual(0, _exit.exception.code)
        # concepts.csv will be extended through one concept from the variables.csv
        TEST_CASE.assertEqual(2, Concept.objects.count())
        concept = Concept.objects.filter(name="some-concept").first()
        TEST_CASE.assertEqual("some-concept", concept.name)
        TEST_CASE.assertEqual("Some concept", concept.label)
        TEST_CASE.assertEqual(topic, concept.topics.first())

        search = ConceptDocument.search().query("match_all")
        TEST_CASE.assertEqual(2, search.count())
        response = search.execute()
        TEST_CASE.assertIn("some-concept", [hit.name for hit in response.hits])
        ConceptDocument.search().query("match_all").delete()

    def test_import_analysis_units(self, study_import_manager):
        TEST_CASE.assertEqual(0, AnalysisUnit.objects.count())
        study_import_manager.import_single_entity("analysis_units")
        TEST_CASE.assertEqual(1, AnalysisUnit.objects.count())
        analysis_unit = AnalysisUnit.objects.first()
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.name)
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.label)
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.description)

    def test_import_periods(self, study_import_manager, study):
        TEST_CASE.assertEqual(0, Period.objects.count())
        study_import_manager.import_single_entity("periods")
        TEST_CASE.assertEqual(1, Period.objects.count())
        period = Period.objects.first()
        TEST_CASE.assertEqual("some-period", period.name)
        TEST_CASE.assertEqual("some-period", period.label)
        TEST_CASE.assertEqual(study, period.study)

    def test_import_conceptual_datasets(self, study_import_manager):
        TEST_CASE.assertEqual(0, ConceptualDataset.objects.count())
        study_import_manager.import_single_entity("conceptual_datasets")
        TEST_CASE.assertEqual(1, ConceptualDataset.objects.count())
        conceptual_dataset = ConceptualDataset.objects.first()
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.name)
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.label)
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.description)

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_instruments(self, study, period, analysis_unit):
        TEST_CASE.assertEqual(0, Instrument.objects.count())
        TEST_CASE.assertEqual(0, Question.objects.count())
        with TEST_CASE.assertRaises(SystemExit) as _error:
            call_command("update", study.name, "instruments", "-l")
            TEST_CASE.assertEqual(0, _error.exception.code)
        TEST_CASE.assertEqual(1, Instrument.objects.count())
        TEST_CASE.assertEqual(1, Question.objects.count())
        instrument = Instrument.objects.first()
        TEST_CASE.assertEqual("some-instrument", instrument.name)
        TEST_CASE.assertEqual(study, instrument.study)
        TEST_CASE.assertEqual(analysis_unit, instrument.analysis_unit)
        TEST_CASE.assertEqual(period, instrument.period)

        call_command("search_index", "--populate")
        search = QuestionDocument.search().query("match_all")
        TEST_CASE.assertEqual(1, search.count())
        response = search.execute()
        hit = response.hits[0]
        # TEST_CASE.assertEqual(study.name, hit.study)
        TEST_CASE.assertEqual("some-question", hit.name)
        TEST_CASE.assertEqual("Some Instrument", hit.instrument)
        QuestionDocument.search().query("match_all").delete()

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_json_datasets(self, study):
        TEST_CASE.assertEqual(0, Dataset.objects.count())
        TEST_CASE.assertEqual(0, Variable.objects.count())
        with TEST_CASE.assertRaises(SystemExit) as _error:
            call_command("update", study.name, "datasets.json", "-l")
            TEST_CASE.assertEqual(0, _error.exception.code)
        TEST_CASE.assertEqual(1, Dataset.objects.count())
        TEST_CASE.assertEqual(2, Variable.objects.count())
        dataset = Dataset.objects.first()

        name = "some-variable"
        variable, created = Variable.objects.get_or_create(name=name)
        TEST_CASE.assertEqual("some-dataset", dataset.name)
        TEST_CASE.assertEqual(study, dataset.study)

        TEST_CASE.assertFalse(created)
        TEST_CASE.assertEqual(name, variable.name)

        search = VariableDocument.search().query("match_all")
        TEST_CASE.assertEqual(2, len(search.execute()))
        VariableDocument.search().query("match_all").delete()

    def test_import_csv_datasets(
        self, dataset, period, analysis_unit, conceptual_dataset
    ):
        with TEST_CASE.assertRaises(SystemExit) as _error:
            call_command("update", dataset.study.name, "datasets.csv", "-l")
        TEST_CASE.assertEqual(0, _error.exception.code)
        TEST_CASE.assertEqual(1, Dataset.objects.count())
        dataset = Dataset.objects.get(name="some-dataset")
        TEST_CASE.assertEqual("some-dataset", dataset.label)
        TEST_CASE.assertEqual("some-dataset", dataset.description)
        TEST_CASE.assertEqual(analysis_unit, dataset.analysis_unit)
        TEST_CASE.assertEqual(period, dataset.period)
        TEST_CASE.assertEqual(conceptual_dataset, dataset.conceptual_dataset)

    def test_import_variables(self, study, variable, concept):
        TEST_CASE.assertEqual(1, Variable.objects.count())
        with TEST_CASE.assertRaises(SystemExit) as _exit:
            call_command("update", study.name, "concepts", "-l")
            TEST_CASE.assertEqual(0, _exit.exception.code)
        with TEST_CASE.assertRaises(SystemExit) as _exit:
            call_command("update", study.name, "variables", "-l")
            TEST_CASE.assertEqual(0, _exit.exception.code)
        TEST_CASE.assertEqual(3, Variable.objects.count())
        imported_variable = Variable.objects.get(
            name=variable.name, dataset=variable.dataset
        )
        TEST_CASE.assertEqual("https://variable-image.de", imported_variable.image_url)
        TEST_CASE.assertEqual(concept, imported_variable.concept)

    @pytest.mark.usefixtures("variable", "concept")
    def test_import_variables_empty_concept(self, study):
        """Do not create concept with empty, "", name."""

        variables_csv = Study().import_path().joinpath("variables.csv")
        with open(variables_csv, "a", encoding="utf8") as file:
            file.write("some-study,some-dataset,a-variable,,")

        TEST_CASE.assertEqual(1, Variable.objects.count())
        with TEST_CASE.assertRaises(SystemExit) as _exit:
            call_command("update", study.name, "concepts", "-l")
            TEST_CASE.assertEqual(0, _exit.exception.code)
        with TEST_CASE.assertRaises(SystemExit) as _exit:
            call_command("update", study.name, "variables", "-l")
            TEST_CASE.assertEqual(0, _exit.exception.code)
        TEST_CASE.assertEqual(2, Concept.objects.count())

    def test_import_questions_variables(self, study_import_manager, variable, question):
        TEST_CASE.assertEqual(0, QuestionVariable.objects.count())
        study_import_manager.import_single_entity("questions_variables")
        TEST_CASE.assertEqual(1, QuestionVariable.objects.count())
        relation = QuestionVariable.objects.first()
        TEST_CASE.assertEqual(variable, relation.variable)
        TEST_CASE.assertEqual(question, relation.question)

    def test_import_concepts_questions(self, study_import_manager, concept, question):
        TEST_CASE.assertEqual(0, ConceptQuestion.objects.count())
        study_import_manager.import_single_entity("concepts_questions")
        TEST_CASE.assertEqual(1, ConceptQuestion.objects.count())
        relation = ConceptQuestion.objects.first()
        TEST_CASE.assertEqual(concept, relation.concept)
        TEST_CASE.assertEqual(question, relation.question)

    def test_import_transformations(self, study_import_manager, variable):
        TEST_CASE.assertEqual(0, Transformation.objects.count())
        other_variable = VariableFactory(name="some-other-variable")
        study_import_manager.import_single_entity("transformations")
        TEST_CASE.assertEqual(1, Transformation.objects.count())
        relation = Transformation.objects.first()
        TEST_CASE.assertEqual(variable, relation.origin)
        TEST_CASE.assertEqual(other_variable, relation.target)

    def test_import_attachments(self, study_import_manager, study):
        TEST_CASE.assertEqual(0, Attachment.objects.count())
        study_import_manager.import_single_entity("attachments")
        TEST_CASE.assertEqual(1, Attachment.objects.count())
        attachment = Attachment.objects.first()
        TEST_CASE.assertEqual(study, attachment.context_study)
        TEST_CASE.assertEqual("https://some-study.de", attachment.url)
        TEST_CASE.assertEqual("some-study", attachment.url_text)

    @pytest.mark.usefixtures("study")
    def test_import_attachments_exception(self, study_import_manager):
        TEST_CASE.assertEqual(0, Attachment.objects.count())
        attachements_path = study_import_manager.study.import_path().joinpath(
            "attachments.csv"
        )
        header = (
            "type",
            "study",
            "dataset",
            "variable",
            "instrument",
            "question",
            "url",
            "url_text",
        )
        row = dict(type="dataset", dataset="Nonexistent-dataset")
        with open(attachements_path, "w", encoding="utf8") as attacheements_file:
            writer = csv.DictWriter(attacheements_file, fieldnames=header)
            writer.writeheader()
            writer.writerow(row)
        with TEST_CASE.assertRaises(Dataset.DoesNotExist) as error:
            study_import_manager.import_single_entity("attachments")
        error_dict = json.loads(error.exception.args[0])
        TEST_CASE.assertDictContainsSubset(row, error_dict)

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_publications(self, study_import_manager, study):
        TEST_CASE.assertEqual(0, Publication.objects.count())
        study_import_manager.import_single_entity("publications")

        TEST_CASE.assertEqual(1, Publication.objects.count())
        publication = Publication.objects.first()
        TEST_CASE.assertEqual("Some Publication", publication.title)
        TEST_CASE.assertEqual("some-doi", publication.doi)
        TEST_CASE.assertEqual(study, publication.study)
        search = PublicationDocument.search().query("match_all")
        TEST_CASE.assertEqual(1, search.count())
        response = search.execute()
        hit = response.hits[0]
        TEST_CASE.assertEqual(study.title(), hit.study)
        TEST_CASE.assertEqual("some-doi", hit.doi)
        TEST_CASE.assertEqual(2018, hit.year)
        PublicationDocument.search().query("match_all").delete()

    @pytest.mark.usefixtures("elasticsearch_indices")
    def test_import_all(self, study):

        call_command("search_index", "--delete", force=True)
        TEST_CASE.assertEqual(1, Study.objects.count())

        TEST_CASE.assertEqual(0, Concept.objects.count())
        TEST_CASE.assertEqual(0, ConceptualDataset.objects.count())
        TEST_CASE.assertEqual(0, Dataset.objects.count())
        TEST_CASE.assertEqual(0, Variable.objects.count())
        TEST_CASE.assertEqual(0, Period.objects.count())
        TEST_CASE.assertEqual(0, Publication.objects.count())
        TEST_CASE.assertEqual(0, Question.objects.count())
        TEST_CASE.assertEqual(0, Transformation.objects.count())
        TEST_CASE.assertEqual(0, Instrument.objects.count())
        TEST_CASE.assertEqual(0, QuestionVariable.objects.count())
        TEST_CASE.assertEqual(0, ConceptQuestion.objects.count())

        with TEST_CASE.assertRaises(SystemExit) as _error:
            call_command("update", study.name, "-l")
            TEST_CASE.assertEqual(0, _error.exception.code)
        TEST_CASE.assertEqual(2, Concept.objects.count())
        TEST_CASE.assertEqual(1, ConceptualDataset.objects.count())
        TEST_CASE.assertEqual(1, Dataset.objects.count())
        TEST_CASE.assertEqual(3, Variable.objects.count())
        TEST_CASE.assertEqual(1, Period.objects.count())
        TEST_CASE.assertEqual(1, Publication.objects.count())
        TEST_CASE.assertEqual(2, Question.objects.count())
        TEST_CASE.assertEqual(1, Transformation.objects.count())
        TEST_CASE.assertEqual(1, Instrument.objects.count())
        TEST_CASE.assertEqual(1, QuestionVariable.objects.count())
        TEST_CASE.assertEqual(1, ConceptQuestion.objects.count())

        concept_search = ConceptDocument.search().query("match_all").execute()
        variable_search = VariableDocument.search().query("match_all").execute()
        publication_search = PublicationDocument.search().query("match_all").execute()
        question_search = QuestionDocument.search().query("match_all").execute()

        TEST_CASE.assertEqual(2, len(concept_search))
        TEST_CASE.assertEqual(3, len(variable_search))
        TEST_CASE.assertEqual(1, len(publication_search))
        TEST_CASE.assertEqual(2, len(question_search))

        ConceptDocument.search().query("match_all").delete()
        VariableDocument.search().query("match_all").delete()
        PublicationDocument.search().query("match_all").delete()
        QuestionDocument.search().query("match_all").delete()

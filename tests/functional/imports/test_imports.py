# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import csv
import json
import unittest
from pathlib import Path
from typing import Any

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
from ddionrails.imports.management.commands.update import update
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
from tests.imports.management_commands.test_update import get_options

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
    call_command("search_index", "--delete", "--no-parallel", force=True)


@pytest.fixture(name="unittest_settings")
def _unittest_settings(request, settings):
    if request.instance:
        request.instance.settings = settings


@pytest.mark.django_db
@pytest.mark.usefixtures("unittest_settings", "tmp_dir")
class TestStudyImportManagerUnittest(unittest.TestCase):
    data_dir: Path
    settings: Any
    study: Study

    def setUp(self) -> None:
        self.settings.IMPORT_REPO_PATH = self.data_dir
        self.study = Study(name="some-study")
        self.study.save()
        self.study_import_manager = StudyImportManager(study=self.study, redis=False)
        return super().setUp()

    def test_import_csv_topics_exception(self):
        import_path: Path = self.study_import_manager.study.import_path()

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

        with self.assertRaises(Study.DoesNotExist):
            options = get_options(self.study.name)
            options["entity"] = "topics.csv"
            update(options)

    def test_import_attachments_exception(self):
        TEST_CASE.assertEqual(0, Attachment.objects.count())
        import_path = self.study_import_manager.study.import_path().joinpath(
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
        row = {"type": "dataset", "dataset": "Nonexistent-dataset"}
        with open(import_path, "w", encoding="utf8") as attachements_file:
            writer = csv.DictWriter(attachements_file, fieldnames=header)
            writer.writeheader()
            writer.writerow(row)
        with TEST_CASE.assertRaises(Dataset.DoesNotExist) as error:
            options = get_options(self.study.name)
            options["entity"] = "attachments"
            update(options)

        error_dict = json.loads(error.exception.args[0])
        for key, value in row.items():
            TEST_CASE.assertEqual(
                error_dict[key], value, msg="Result is not fully contained in expected."
            )

    def test_import_attachments(self):
        TEST_CASE.assertEqual(0, Attachment.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "attachments"
        update(options)

        TEST_CASE.assertEqual(1, Attachment.objects.count())
        attachment = Attachment.objects.first()
        TEST_CASE.assertEqual(self.study, attachment.context_study)
        TEST_CASE.assertEqual("https://some-study.de", attachment.url)
        TEST_CASE.assertEqual("some-study", attachment.url_text)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_import_path", "clean_search_index")
class TestStudyImportManager:
    def test_import_study(self, study_import_manager):  # pylint: disable=unused-argument

        options = get_options(study_import_manager.study.name)
        options["entity"] = "study"
        update(options)

        TEST_CASE.assertEqual(1, Study.objects.count())
        # refresh
        study = Study.objects.first()
        TEST_CASE.assertEqual("Some Study", study.label)
        TEST_CASE.assertEqual({"variables": {"label-table": True}}, study.config)

    def test_import_csv_topics(self, study_import_manager):
        TEST_CASE.assertEqual(0, Topic.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "topics.csv"
        update(options)

        TEST_CASE.assertEqual(2, Topic.objects.count())
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        TEST_CASE.assertEqual("some-label", topic.label)
        TEST_CASE.assertEqual(parent_topic, topic.parent)
        TEST_CASE.assertEqual("some-other-label", parent_topic.label)

    def test_import_json_topics(
        self, study_import_manager
    ):  # pylint: disable=unused-argument
        TEST_CASE.assertEqual(1, Study.objects.count())
        TEST_CASE.assertEqual(0, Topic.objects.count())
        TEST_CASE.assertEqual(0, TopicList.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "study"
        update(options)
        options["entity"] = "topics.json"
        update(options)

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

        options = get_options(study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        # concepts.csv will be extended through one concept from the variables.csv
        TEST_CASE.assertEqual(2, Concept.objects.count())
        concept = Concept.objects.filter(name="some-concept").first()
        TEST_CASE.assertEqual("some-concept", concept.name)
        TEST_CASE.assertEqual("Some concept", concept.label)

        for concept in Concept.objects.all():
            concept.save()
        search = ConceptDocument.search().query("match_all")
        TEST_CASE.assertEqual(2, search.count())
        response = search.execute()
        TEST_CASE.assertIn("some-concept", [hit.name for hit in response.hits])
        ConceptDocument.search().query("match_all").delete()

    def test_import_analysis_units(self, study_import_manager):
        TEST_CASE.assertEqual(0, AnalysisUnit.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "analysis_units"
        update(options)

        TEST_CASE.assertEqual(1, AnalysisUnit.objects.count())
        analysis_unit = AnalysisUnit.objects.first()
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.name)
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.label)
        TEST_CASE.assertEqual("some-analysis-unit", analysis_unit.description)

    def test_import_periods(self, study_import_manager, study):
        TEST_CASE.assertEqual(0, Period.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "periods"
        update(options)

        TEST_CASE.assertEqual(1, Period.objects.count())
        period = Period.objects.first()
        TEST_CASE.assertEqual("some-period", period.name)
        TEST_CASE.assertEqual("some-period", period.label)
        TEST_CASE.assertEqual(self.study, period.study)

    def test_import_conceptual_datasets(self, study_import_manager):
        TEST_CASE.assertEqual(0, ConceptualDataset.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "conceptual_datasets"
        update(options)

        TEST_CASE.assertEqual(1, ConceptualDataset.objects.count())
        conceptual_dataset = ConceptualDataset.objects.first()
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.name)
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.label)
        TEST_CASE.assertEqual("some-conceptual-dataset", conceptual_dataset.description)

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_instruments(self, study, period, analysis_unit):
        TEST_CASE.assertEqual(0, Instrument.objects.count())
        TEST_CASE.assertEqual(0, Question.objects.count())

        options = get_options(study.name)
        options["entity"] = "instruments.json"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        TEST_CASE.assertEqual(1, Instrument.objects.count())
        TEST_CASE.assertEqual(1, Question.objects.count())
        instrument = Instrument.objects.first()
        TEST_CASE.assertEqual("some-instrument", instrument.name)
        TEST_CASE.assertEqual(study, instrument.study)

        call_command("search_index", "--populate", "--no-parallel")
        search = QuestionDocument.search().query("match_all")
        TEST_CASE.assertEqual(1, search.count())
        response = search.execute()
        hit = response.hits[0]
        TEST_CASE.assertEqual(study.name, hit.study["name"])
        TEST_CASE.assertEqual("some-question", hit.name)
        TEST_CASE.assertEqual("Some Instrument", hit.instrument["label"])
        QuestionDocument.search().query("match_all").delete()

    def test_import_json_datasets(self, study):
        TEST_CASE.assertEqual(0, Dataset.objects.count())
        TEST_CASE.assertEqual(0, Variable.objects.count())

        options = get_options(study.name)
        options["entity"] = "datasets.json"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

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
        options = get_options(dataset.study.name)
        options["entity"] = "datasets.csv"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)
        TEST_CASE.assertEqual(1, Dataset.objects.count())
        dataset = Dataset.objects.get(name="some-dataset")
        TEST_CASE.assertEqual("some-dataset", dataset.label)
        TEST_CASE.assertEqual("some-dataset", dataset.description)
        TEST_CASE.assertEqual(analysis_unit, dataset.analysis_unit)
        TEST_CASE.assertEqual(period, dataset.period)
        TEST_CASE.assertEqual(conceptual_dataset, dataset.conceptual_dataset)

    def test_import_variables(self, study, variable, concept):
        TEST_CASE.assertEqual(1, Variable.objects.count())

        options = get_options(study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        options["entity"] = "variables"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        TEST_CASE.assertEqual(3, Variable.objects.count())
        imported_variable = Variable.objects.get(
            name=variable.name, dataset=variable.dataset
        )
        TEST_CASE.assertEqual("https://variable-image.de", imported_variable.image_url)
        TEST_CASE.assertEqual("some-concept", imported_variable.concept.name)

    @pytest.mark.usefixtures("variable", "concept")
    def test_import_variables_empty_concept(self, study):
        """Do not create concept with empty, "", name."""

        variables_csv = Study().import_path().joinpath("variables.csv")
        with open(variables_csv, "a", encoding="utf8") as file:
            file.write("some-study,some-dataset,a-variable,,")

        TEST_CASE.assertEqual(1, Variable.objects.count())

        options = get_options(study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        options["entity"] = "variables"
        _, error = update(options)
        TEST_CASE.assertIsNone(error)

        TEST_CASE.assertEqual(2, Concept.objects.count())

    def test_import_questions_variables(self, study_import_manager, variable, question):
        TEST_CASE.assertEqual(0, QuestionVariable.objects.count())
        some_variable = Variable(dataset=variable.dataset, name="some-other-variable")
        some_variable.save()

        options = get_options(study_import_manager.study.name)
        options["entity"] = "questions"
        update(options)
        options["entity"] = "questions_variables"
        update(options)

        question_variables = list(QuestionVariable.objects.all())
        TEST_CASE.assertEqual(2, len(question_variables))
        relation = QuestionVariable.objects.get(variable=variable)
        TEST_CASE.assertEqual(variable, relation.variable)
        TEST_CASE.assertEqual(question, relation.question)

    def test_import_concepts_questions(self, study_import_manager, concept, question):
        TEST_CASE.assertEqual(0, ConceptQuestion.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "concepts_questions"
        update(options)

        TEST_CASE.assertEqual(1, ConceptQuestion.objects.count())
        relation = ConceptQuestion.objects.first()
        TEST_CASE.assertEqual(concept, relation.concept)
        TEST_CASE.assertEqual(question, relation.question)

    def test_import_transformations(self, study_import_manager, variable):
        TEST_CASE.assertEqual(0, Transformation.objects.count())
        other_variable = VariableFactory(name="some-other-variable")

        options = get_options(study_import_manager.study.name)
        options["entity"] = "transformations"
        update(options)

        TEST_CASE.assertEqual(1, Transformation.objects.count())
        relation = Transformation.objects.first()
        TEST_CASE.assertEqual(variable, relation.origin)
        TEST_CASE.assertEqual(other_variable, relation.target)

    @pytest.mark.usefixtures(("elasticsearch_indices"))
    def test_import_publications(self, study_import_manager, study):
        TEST_CASE.assertEqual(0, Publication.objects.count())

        options = get_options(study_import_manager.study.name)
        options["entity"] = "publications"
        update(options)

        TEST_CASE.assertEqual(1, Publication.objects.count())
        publication = Publication.objects.first()
        TEST_CASE.assertEqual("Some Publication", publication.title)
        TEST_CASE.assertEqual("some-doi", publication.doi)
        TEST_CASE.assertEqual(study, publication.study)
        search = PublicationDocument.search().query("match_all")
        TEST_CASE.assertEqual(1, search.count())
        response = search.execute()
        hit = response.hits[0]
        TEST_CASE.assertEqual(study.title(), hit.study_name)
        TEST_CASE.assertEqual("some-doi", hit.doi)
        TEST_CASE.assertEqual(2018, int(hit.year))
        PublicationDocument.search().query("match_all").delete()

    @pytest.mark.usefixtures("elasticsearch_indices")
    def test_import_all(self, study):
        call_command("search_index", "--delete", "--no-parallel", force=True)
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

        options = get_options(study.name)
        _, errors = update(options)
        TEST_CASE.assertIsNone(errors)

        TEST_CASE.assertEqual(2, Concept.objects.count())
        TEST_CASE.assertEqual(1, ConceptualDataset.objects.count())
        TEST_CASE.assertEqual(1, Dataset.objects.count())
        TEST_CASE.assertEqual(3, Variable.objects.count())
        TEST_CASE.assertEqual(1, Period.objects.count())
        TEST_CASE.assertEqual(1, Publication.objects.count())
        TEST_CASE.assertEqual(2, Question.objects.count())
        TEST_CASE.assertEqual(1, Transformation.objects.count())
        TEST_CASE.assertEqual(1, Instrument.objects.count())
        TEST_CASE.assertEqual(2, QuestionVariable.objects.count())
        TEST_CASE.assertEqual(1, ConceptQuestion.objects.count())

        for concept in Concept.objects.all():
            concept.save()
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

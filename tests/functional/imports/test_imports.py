# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import csv
import json
from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command
from django.test import LiveServerTestCase, override_settings

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
from tests.functional.search_index_fixtures import set_up_index, tear_down_index
from tests.imports.management_commands.test_update import get_options

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.filterwarnings("ignore::DeprecationWarning")
]


@pytest.fixture(name="study_import_manager")
def _study_import_manager(study, settings, request):
    settings.IMPORT_REPO_PATH = Path("tests/functional/test_data/")
    manager = StudyImportManager(study)
    if request.instance:
        request.instance.study_import_manager = manager
    yield manager


@pytest.fixture(name="clean_search_index")
def _clean_search_index():
    yield
    call_command("search_index", "--delete", "--no-parallel", force=True)


@pytest.fixture(name="unittest_settings")
def _unittest_settings(request, settings):
    if request.instance:
        request.instance.settings = settings


@pytest.mark.usefixtures("mock_import_path", "clean_search_index")
@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
@pytest.mark.usefixtures(
    "analysis_unit",
    "concept",
    "conceptual_dataset",
    "dataset",
    "period",
    "question",
    "study",
    "study_import_manager",
    "topic",
    "variable",
)
class TestStudyImportManager(LiveServerTestCase):
    analysis_unit: Any
    concept: Any
    conceptual_dataset: Any
    dataset: Any
    period: Any
    question: Any
    study: Study
    study_import_manager: Any
    topic: Any
    variable: Any

    def setUp(self) -> None:
        self.publication = Publication.objects.create(
            name="some-publication",
            title="Some Publication",
            study=self.study,
            type="book",
            year=2019,
        )
        set_up_index(self, self.concept, "concepts")
        set_up_index(self, self.publication, "publications")
        set_up_index(self, self.question, "questions")
        set_up_index(self, self.topic, "topics")
        set_up_index(self, self.variable, "variables")
        return super().setUp()

    def tearDown(self) -> None:
        tear_down_index(self, "concepts")
        tear_down_index(self, "publications")
        tear_down_index(self, "questions")
        tear_down_index(self, "topics")
        tear_down_index(self, "variables")
        return super().tearDown()

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
        self.assertEqual(0, Attachment.objects.count())
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
        with self.assertRaises(Dataset.DoesNotExist) as error:
            options = get_options(self.study.name)
            options["entity"] = "attachments"
            update(options)

        error_dict = json.loads(error.exception.args[0])
        for key, value in row.items():
            self.assertEqual(
                error_dict[key], value, msg="Result is not fully contained in expected."
            )

    def test_import_attachments(self):
        self.assertEqual(0, Attachment.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "attachments"
        update(options)

        self.assertEqual(1, Attachment.objects.count())
        attachment = Attachment.objects.first()
        self.assertEqual(self.study, attachment.context_study)
        self.assertEqual("https://some-study.de", attachment.url)
        self.assertEqual("some-study", attachment.url_text)

    def test_import_study(self):  # pylint: disable=unused-argument

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "study"
        update(options)

        self.assertEqual(1, Study.objects.count())
        # refresh
        study = Study.objects.first()
        self.assertEqual("Some Study", study.label)
        self.assertEqual({"variables": {"label-table": True}}, study.config)

    def test_import_csv_topics(self):
        topic_count = Topic.objects.count()

        self.assertEqual(2, topic_count)

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "topics.csv"
        update(options)

        self.assertEqual(3, Topic.objects.count())
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        self.assertEqual("some-label", topic.label)
        self.assertEqual(parent_topic, topic.parent)
        self.assertEqual("some-other-label", parent_topic.label)

    def test_import_json_topics(self):  # pylint: disable=unused-argument
        self.assertEqual(1, Study.objects.count())
        self.assertEqual(2, Topic.objects.count())
        self.assertEqual(0, TopicList.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "study"
        update(options)
        options["entity"] = "topics.json"
        update(options)

        self.assertEqual(1, Study.objects.count())
        self.assertEqual(1, TopicList.objects.count())
        study = Study.objects.first()
        topiclist = TopicList.objects.first()
        self.assertEqual(study, topiclist.study)
        english_topics = topiclist.topiclist[0]
        self.assertEqual("en", english_topics["language"])
        german_topics = topiclist.topiclist[1]
        self.assertEqual("de", german_topics["language"])

    def test_import_concepts(self):
        self.assertEqual(1, Concept.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)

        # concepts.csv will be extended through one concept from the variables.csv
        self.assertEqual(2, Concept.objects.count())
        concept = Concept.objects.filter(name="some-concept").first()
        self.assertEqual("some-concept", concept.name)
        self.assertEqual("Some concept", concept.label)

        set_up_index(self, Concept.objects.all(), "concepts")
        search = ConceptDocument.search().query("match_all")

        self.assertEqual(2, search.count())
        response = search.execute()
        self.assertIn("some-concept", [hit.name for hit in response.hits])

    def test_import_analysis_units(self):
        self.assertEqual(1, AnalysisUnit.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "analysis_units"
        update(options)

        self.assertEqual(1, AnalysisUnit.objects.count())
        analysis_unit = AnalysisUnit.objects.first()
        self.assertEqual("some-analysis-unit", analysis_unit.name)
        self.assertEqual("some-analysis-unit", analysis_unit.label)
        self.assertEqual("some-analysis-unit", analysis_unit.description)

    def test_import_periods(self):
        self.assertEqual(1, Period.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "periods"
        update(options)

        self.assertEqual(1, Period.objects.count())
        period = Period.objects.first()
        self.assertEqual("some-period", period.name)
        self.assertEqual("some-period", period.label)
        self.assertEqual(self.study, period.study)

    def test_import_conceptual_datasets(self):
        self.assertEqual(1, ConceptualDataset.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "conceptual_datasets"
        update(options)

        self.assertEqual(1, ConceptualDataset.objects.count())
        conceptual_dataset = ConceptualDataset.objects.first()
        self.assertEqual("some-conceptual-dataset", conceptual_dataset.name)
        self.assertEqual("some-conceptual-dataset", conceptual_dataset.label)
        self.assertEqual("some-conceptual-dataset", conceptual_dataset.description)

    def test_import_instruments(self):
        self.assertEqual(1, Instrument.objects.count())
        self.assertEqual(1, Question.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "instruments.json"
        _, error = update(options)
        self.assertIsNone(error)

        self.assertEqual(1, Instrument.objects.count())
        self.assertEqual(1, Question.objects.count())
        instrument = Instrument.objects.first()
        self.assertEqual("some-instrument", instrument.name)
        self.assertEqual(self.study, instrument.study)

        call_command("search_index", "--populate", "--no-parallel")
        search = QuestionDocument.search().query("match_all")
        self.assertEqual(1, search.count())
        response = search.execute()
        hit = response.hits[0]
        self.assertEqual(self.study.name, hit.study["name"])
        self.assertEqual("some-question", hit.name)
        self.assertEqual("Some Instrument", hit.instrument["label"])

    def test_import_json_datasets(self):
        self.assertEqual(1, Dataset.objects.count())
        self.assertEqual(1, Variable.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "datasets.json"
        _, error = update(options)
        self.assertIsNone(error)

        self.assertEqual(1, Dataset.objects.count())
        self.assertEqual(2, Variable.objects.count())
        dataset = Dataset.objects.first()

        name = "some-variable"
        variable, created = Variable.objects.get_or_create(name=name)
        self.assertEqual("some-dataset", dataset.name)
        self.assertEqual(self.study, dataset.study)

        self.assertFalse(created)
        self.assertEqual(name, variable.name)

        set_up_index(self, Variable.objects.all(), "variables")

        search = VariableDocument.search().query("match_all")
        self.assertEqual(2, len(search.execute()))

    def test_import_csv_datasets(self):
        options = get_options(self.dataset.study.name)
        options["entity"] = "datasets.csv"
        _, error = update(options)
        self.assertIsNone(error)
        self.assertEqual(1, Dataset.objects.count())
        dataset = Dataset.objects.get(name="some-dataset")
        self.assertEqual("some-dataset", dataset.label)
        self.assertEqual("some-dataset", dataset.description)
        self.assertEqual(self.analysis_unit, dataset.analysis_unit)
        self.assertEqual(self.period, dataset.period)
        self.assertEqual(self.conceptual_dataset, dataset.conceptual_dataset)

    def test_import_variables(self):
        self.assertEqual(1, Variable.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)

        options["entity"] = "variables"
        _, error = update(options)
        self.assertIsNone(error)

        self.assertEqual(3, Variable.objects.count())
        imported_variable = Variable.objects.get(
            name=self.variable.name, dataset=self.variable.dataset
        )
        self.assertEqual("https://variable-image.de", imported_variable.image_url)
        self.assertEqual("some-concept", imported_variable.concept.name)

    def test_import_variables_empty_concept(self):
        """Do not create concept with empty, "", name."""

        variables_csv = Study().import_path().joinpath("variables.csv")
        with open(variables_csv, "a", encoding="utf8") as file:
            file.write("some-study,some-dataset,a-variable,,")

        self.assertEqual(1, Variable.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)

        options["entity"] = "variables"
        _, error = update(options)
        self.assertIsNone(error)

        self.assertEqual(2, Concept.objects.count())

    def test_import_questions_variables(self):
        self.assertEqual(0, QuestionVariable.objects.count())
        some_variable = Variable(
            dataset=self.variable.dataset, name="some-other-variable"
        )
        some_variable.save()

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "questions"
        update(options)
        options["entity"] = "questions_variables"
        update(options)

        question_variables = list(QuestionVariable.objects.all())
        self.assertEqual(2, len(question_variables))
        relation = QuestionVariable.objects.get(variable=self.variable)
        self.assertEqual(self.variable, relation.variable)
        self.assertEqual(self.question, relation.question)

    def test_import_concepts_questions(self):
        self.assertEqual(0, ConceptQuestion.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "concepts_questions"
        update(options)

        self.assertEqual(1, ConceptQuestion.objects.count())
        relation = ConceptQuestion.objects.first()
        if relation:
            self.assertEqual(self.concept, relation.concept)
            self.assertEqual(self.question, relation.question)
        self.assertIsNotNone(relation)

    def test_import_transformations(self):
        self.assertEqual(0, Transformation.objects.count())
        other_variable = VariableFactory(name="some-other-variable")

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "transformations"
        update(options)

        self.assertEqual(1, Transformation.objects.count())
        relation = Transformation.objects.first()
        if relation:
            self.assertEqual(self.variable, relation.origin)
            self.assertEqual(other_variable, relation.target)
        self.assertIsNotNone(relation)

    def test_import_publications(self):
        self.assertEqual(1, Publication.objects.count())
        Publication.objects.all().delete()

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "publications"
        update(options)

        self.assertEqual(1, Publication.objects.count())
        set_up_index(self, Publication.objects.all(), "publications")
        publication = Publication.objects.get(doi="some-doi")
        self.assertEqual("Some Publication", publication.title)
        self.assertEqual(self.study, publication.study)
        search = PublicationDocument.search().query("match_all")
        self.assertEqual(1, search.count())
        response = search.execute()
        hit_count = 0
        for hit in response.hits:
            if (
                self.study.title() == hit.study_name
                and "some-doi" == hit.doi
                and 2018 == int(hit.year)
            ):
                hit_count = hit_count + 1
        self.assertEqual(1, hit_count)


@pytest.mark.usefixtures("mock_import_path", "clean_search_index")
@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
@pytest.mark.usefixtures(
    "study",
)
class ImportAll(LiveServerTestCase):
    study: Study

    def tearDown(self) -> None:
        tear_down_index(self, "concepts")
        tear_down_index(self, "publications")
        tear_down_index(self, "questions")
        tear_down_index(self, "topics")
        tear_down_index(self, "variables")
        return super().tearDown()

    def test_import_all(self):
        call_command("search_index", "--delete", "--no-parallel", force=True)
        self.assertEqual(1, Study.objects.count())

        self.assertEqual(0, Concept.objects.count())
        self.assertEqual(0, ConceptualDataset.objects.count())
        self.assertEqual(0, Dataset.objects.count())
        self.assertEqual(0, Variable.objects.count())
        self.assertEqual(0, Period.objects.count())
        self.assertEqual(0, Publication.objects.count())
        self.assertEqual(0, Question.objects.count())
        self.assertEqual(0, Transformation.objects.count())
        self.assertEqual(0, Instrument.objects.count())
        self.assertEqual(0, QuestionVariable.objects.count())
        self.assertEqual(0, ConceptQuestion.objects.count())

        options = get_options(self.study.name)
        _, errors = update(options)
        self.assertIsNone(errors)

        set_up_index(self, Concept.objects.all(), "concepts")
        set_up_index(self, Publication.objects.all(), "publications")
        set_up_index(self, Question.objects.all(), "questions")
        set_up_index(self, Topic.objects.all(), "topics")
        set_up_index(self, Variable.objects.all(), "variables")

        self.assertEqual(2, Concept.objects.count())
        self.assertEqual(1, ConceptualDataset.objects.count())
        self.assertEqual(1, Dataset.objects.count())
        self.assertEqual(3, Variable.objects.count())
        self.assertEqual(1, Period.objects.count())
        self.assertEqual(1, Publication.objects.count())
        self.assertEqual(2, Question.objects.count())
        self.assertEqual(1, Transformation.objects.count())
        self.assertEqual(1, Instrument.objects.count())
        self.assertEqual(2, QuestionVariable.objects.count())
        self.assertEqual(1, ConceptQuestion.objects.count())

        for concept in Concept.objects.all():
            concept.save()
        concept_search = ConceptDocument.search().query("match_all").execute()
        variable_search = VariableDocument.search().query("match_all").execute()
        publication_search = PublicationDocument.search().query("match_all").execute()
        question_search = QuestionDocument.search().query("match_all").execute()

        self.assertEqual(2, len(concept_search))
        self.assertEqual(3, len(variable_search))
        self.assertEqual(1, len(publication_search))
        self.assertEqual(2, len(question_search))

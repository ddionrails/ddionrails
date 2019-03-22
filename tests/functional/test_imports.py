import json
import time

import pytest
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period, Topic
from data.models import Dataset, Transformation, Variable
from imports.manager import StudyImportManager
from instruments.models import ConceptQuestion, Instrument, Question, QuestionVariable
from publications.models import Attachment, Publication
from studies.models import Study
from tests.data.factories import VariableFactory

pytestmark = [pytest.mark.functional]


@pytest.fixture()
def es_client(settings):
    mapping_file = "elastic/mapping.json"
    with open(mapping_file, "r") as f:
        mapping = json.loads(f.read())
    es = Elasticsearch()
    # workaround to delete existing index

    # settings.INDEX_NAME = "testing"

    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])
    es.indices.create(index=settings.INDEX_NAME, ignore=400, body=mapping)

    # wait for elastic search index to be created
    time.sleep(0.1)
    yield es
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


@pytest.fixture
def study_import_manager(study, settings):
    settings.IMPORT_REPO_PATH = "tests/functional/test_data/"
    manager = StudyImportManager(study)
    return manager


class TestStudyImportManager:
    def test_import_study(self, study_import_manager, es_client):
        study_import_manager.import_single_entity("study")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Study.objects.count()
        # refresh
        study = Study.objects.first()
        assert "Some Study" == study.label
        assert '{"variables": {"label-table": true}}' == study.config

        s = Search(using=es_client).doc_type("study").query("match", name="some-study")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert "some-study" == hit.name

    def test_import_csv_topics(self, study_import_manager):
        assert 0 == Topic.objects.count()
        study_import_manager.import_single_entity("topics.csv")
        assert 2 == Topic.objects.count()
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        assert "some-topic" == topic.label
        assert parent_topic == topic.parent
        assert "some-other-topic" == parent_topic.label

    def test_import_json_topics(self, study_import_manager, es_client):
        assert 1 == Study.objects.count()
        assert 0 == Topic.objects.count()
        study_import_manager.import_single_entity("study")
        time.sleep(1)
        study_import_manager.import_single_entity("topics.json")
        time.sleep(1)
        s = Search(using=es_client).doc_type("study")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert ["de", "en"] == hit.topic_languages
        s = Search(using=es_client).doc_type("topiclist")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert "en" == hit.topiclist[0]["language"]
        assert "de" == hit.topiclist[1]["language"]

    def test_import_concepts(self, study_import_manager, es_client, topic):
        assert 0 == Concept.objects.count()
        study_import_manager.import_single_entity("concepts")
        assert 1 == Concept.objects.count()
        concept = Concept.objects.first()
        assert "some-concept" == concept.name
        assert "Some concept" == concept.label
        assert topic == concept.topics.first()

        concept.index()
        # wait for indexing to complete
        time.sleep(1)
        s = Search(using=es_client).doc_type("concept")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert "some-concept" == hit.name

    def test_import_analysis_units(self, study_import_manager):
        assert 0 == AnalysisUnit.objects.count()
        study_import_manager.import_single_entity("analysis_units")
        assert 1 == AnalysisUnit.objects.count()
        analysis_unit = AnalysisUnit.objects.first()
        assert "some-analysis-unit" == analysis_unit.name
        assert "some-analysis-unit" == analysis_unit.label
        assert "some-analysis-unit" == analysis_unit.description

    def test_import_periods(self, study_import_manager, study):
        assert 0 == Period.objects.count()
        study_import_manager.import_single_entity("periods")
        assert 1 == Period.objects.count()
        period = Period.objects.first()
        assert "some-period" == period.name
        assert "some-period" == period.label
        assert study == period.study

    def test_import_conceptual_datasets(self, study_import_manager):
        assert 0 == ConceptualDataset.objects.count()
        study_import_manager.import_single_entity("conceptual_datasets")
        assert 1 == ConceptualDataset.objects.count()
        conceptual_dataset = ConceptualDataset.objects.first()
        assert "some-conceptual-dataset" == conceptual_dataset.name
        assert "some-conceptual-dataset" == conceptual_dataset.label
        assert "some-conceptual-dataset" == conceptual_dataset.description

    def test_import_instruments(self, study_import_manager, es_client, study, period):
        assert 0 == Instrument.objects.count()
        assert 0 == Question.objects.count()
        study_import_manager.import_single_entity("instruments")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Instrument.objects.count()
        assert 1 == Question.objects.count()
        instrument = Instrument.objects.first()
        assert "some-instrument" == instrument.name
        assert study == instrument.study
        assert period == instrument.period

        s = Search(using=es_client).doc_type("question")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert study.name == hit.study
        assert "some-question" == hit.name
        assert "some-instrument" == hit.instrument

    def test_import_json_datasets(self, study_import_manager, es_client, study):
        assert 0 == Dataset.objects.count()
        assert 0 == Variable.objects.count()
        study_import_manager.import_single_entity("datasets.json")
        # wait for indexing to complete
        time.sleep(1)
        assert 1 == Dataset.objects.count()
        assert 2 == Variable.objects.count()
        dataset = Dataset.objects.first()
        variable = Variable.objects.first()
        assert "some-dataset" == dataset.name
        assert study == dataset.study
        assert "some-variable" == variable.name

        s = Search(using=es_client).doc_type("variable")
        assert 2 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert study.name == hit.study
        assert "some-variable" == hit.name
        assert "some-dataset" == hit.dataset

    def test_import_csv_datasets(
        self, study_import_manager, dataset, period, analysis_unit, conceptual_dataset
    ):
        study_import_manager.import_single_entity("datasets.csv")
        assert 1 == Dataset.objects.count()
        dataset = Dataset.objects.first()
        assert "some-dataset" == dataset.label
        assert "some-dataset" == dataset.description
        assert analysis_unit == dataset.analysis_unit
        assert period == dataset.period
        assert conceptual_dataset == dataset.conceptual_dataset

    def test_import_variables(self, study_import_manager, variable, concept):
        assert 1 == Variable.objects.count()
        study_import_manager.import_single_entity("variables")
        assert 1 == Variable.objects.count()
        variable = Variable.objects.first()
        assert "https://variable-image.de" == variable.image_url
        assert concept == variable.concept

    def test_import_questions_variables(self, study_import_manager, variable, question):
        assert 0 == QuestionVariable.objects.count()
        study_import_manager.import_single_entity("questions_variables")
        assert 1 == QuestionVariable.objects.count()
        relation = QuestionVariable.objects.first()
        assert variable == relation.variable
        assert question == relation.question

    def test_import_concepts_questions(self, study_import_manager, concept, question):
        assert 0 == ConceptQuestion.objects.count()
        study_import_manager.import_single_entity("concepts_questions")
        assert 1 == ConceptQuestion.objects.count()
        relation = ConceptQuestion.objects.first()
        assert concept == relation.concept
        assert question == relation.question

    def test_import_transformations(self, study_import_manager, variable):
        assert 0 == Transformation.objects.count()
        other_variable = VariableFactory(name="some-other-variable")
        study_import_manager.import_single_entity("transformations")
        assert 1 == Transformation.objects.count()
        relation = Transformation.objects.first()
        assert variable == relation.origin
        assert other_variable == relation.target

    def test_import_attachments(self, study_import_manager, study):
        assert 0 == Attachment.objects.count()
        study_import_manager.import_single_entity("attachments")
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()
        assert study == attachment.context_study
        assert "https://some-study.de" == attachment.url
        assert "some-study" == attachment.url_text

    def test_import_publications(self, study_import_manager, es_client, study):
        assert 0 == Publication.objects.count()
        study_import_manager.import_single_entity("publications")
        # wait for indexing to complete
        time.sleep(1)

        assert 1 == Publication.objects.count()
        publication = Publication.objects.first()
        assert "Some Publication" == publication.title
        assert "some-doi" == publication.doi
        assert study == publication.study
        s = Search(using=es_client).doc_type("publication")
        assert 1 == s.count()
        response = s.execute()
        hit = response.hits[0]
        assert study.name == hit.study
        assert "some-doi" == hit.doi
        assert "2018" == hit.year

    def test_import_all(self, study_import_manager, es_client):
        assert 1 == Study.objects.count()

        assert 0 == Concept.objects.count()
        assert 0 == ConceptualDataset.objects.count()
        assert 0 == Dataset.objects.count()
        assert 0 == Variable.objects.count()
        assert 0 == Period.objects.count()
        assert 0 == Publication.objects.count()
        assert 0 == Question.objects.count()
        assert 0 == Transformation.objects.count()
        assert 0 == Instrument.objects.count()
        assert 0 == QuestionVariable.objects.count()
        assert 0 == ConceptQuestion.objects.count()

        study_import_manager.import_all_entities()
        time.sleep(1)

        assert 1 == Concept.objects.count()
        assert 1 == ConceptualDataset.objects.count()
        assert 1 == Dataset.objects.count()
        assert 2 == Variable.objects.count()
        assert 1 == Period.objects.count()
        assert 1 == Publication.objects.count()
        assert 1 == Question.objects.count()
        assert 1 == Transformation.objects.count()
        assert 1 == Instrument.objects.count()
        assert 1 == QuestionVariable.objects.count()
        assert 1 == ConceptQuestion.objects.count()

        s = Search(using=es_client).doc_type("study")
        assert 1 == s.count()

        # Concepts will be indexed when mgmt command "upgrade" is called

        # s = Search(using=es_client).doc_type("concept")
        # assert 1 == s.count()
        s = Search(using=es_client).doc_type("variable")
        assert 2 == s.count()
        s = Search(using=es_client).doc_type("publication")
        assert 1 == s.count()

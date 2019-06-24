# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use

import time
from pathlib import Path

import pytest
from django.forms.models import model_to_dict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

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

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.functional,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]


@pytest.fixture
def study_import_manager(study, settings):
    settings.IMPORT_REPO_PATH = Path("tests/functional/test_data/")
    manager = StudyImportManager(study)
    return manager


class TestStudyImportManager:
    def test_import_study(self, study_import_manager):  # pylint: disable=unused-argument
        study_import_manager.import_single_entity("study")
        assert 1 == Study.objects.count()
        # refresh
        study_import_manager.study.refresh_from_db()
        expected = "Some Study"
        assert expected == study_import_manager.study.label
        expected = {"variables": {"label-table": True}}
        assert expected == study_import_manager.study.config

    def test_import_csv_topics(self, study_import_manager):
        assert 0 == Topic.objects.count()
        study_import_manager.import_single_entity("topics.csv")
        assert 2 == Topic.objects.count()
        topic = Topic.objects.get(name="some-topic")
        parent_topic = Topic.objects.get(name="some-other-topic")
        assert "some-topic" == topic.label
        assert parent_topic == topic.parent
        assert "some-other-topic" == parent_topic.label

    def test_import_json_topics(
        self, study_import_manager
    ):  # pylint: disable=unused-argument
        assert 1 == Study.objects.count()
        assert 0 == Topic.objects.count()
        assert 0 == TopicList.objects.count()
        study_import_manager.import_single_entity("study")
        study_import_manager.import_single_entity("topics.json")
        assert 1 == Study.objects.count()
        assert 1 == TopicList.objects.count()
        study = Study.objects.first()
        topiclist = TopicList.objects.first()
        assert study == topiclist.study
        english_topics = topiclist.topiclist[0]
        assert "en" == english_topics["language"]
        german_topics = topiclist.topiclist[1]
        assert "de" == german_topics["language"]

    def test_import_concepts(self, study_import_manager, elasticsearch_indices, topic):
        assert 0 == Concept.objects.count()
        study_import_manager.import_single_entity("concepts")
        assert 1 == Concept.objects.count()
        concept = Concept.objects.first()
        assert "some-concept" == concept.name
        assert "Some concept" == concept.label
        assert topic == concept.topics.first()

        search = ConceptDocument.search().query("match_all")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert "some-concept" == hit.name
        ConceptDocument.search().query("match_all").delete()

    def test_import_analysis_units(self, study_import_manager):
        assert 0 == AnalysisUnit.objects.count()
        study_import_manager.import_single_entity("analysis_units")
        assert 1 == AnalysisUnit.objects.count()
        analysis_unit = AnalysisUnit.objects.first()
        exptected = {
            "name": "some-analysis-unit",
            "label": "some-analysis-unit",
            "label_de": "some-analysis-unit",
            "description": "some-analysis-unit",
            "description_de": "some-analysis-unit",
            "study": study_import_manager.study.id,
        }
        result = model_to_dict(
            analysis_unit,
            fields=(
                "name",
                "label",
                "label_de",
                "description",
                "description_de",
                "study",
            ),
        )
        assert exptected == result

    def test_import_periods(self, study_import_manager, study):
        assert 0 == Period.objects.count()
        study_import_manager.import_single_entity("periods")
        assert 1 == Period.objects.count()
        period = Period.objects.first()
        exptected = {
            "name": "some-period",
            "label": "some-period",
            "label_de": "some-period",
            "description": "some-period",
            "description_de": "some-period",
            "study": study_import_manager.study.id,
        }
        result = model_to_dict(
            period,
            fields=(
                "name",
                "label",
                "label_de",
                "description",
                "description_de",
                "study",
            ),
        )
        assert exptected == result

    def test_import_conceptual_datasets(self, study_import_manager):
        assert 0 == ConceptualDataset.objects.count()
        study_import_manager.import_single_entity("conceptual_datasets")
        assert 1 == ConceptualDataset.objects.count()
        conceptual_dataset = ConceptualDataset.objects.first()
        exptected = {
            "name": "some-conceptual-dataset",
            "label": "some-conceptual-dataset",
            "label_de": "some-conceptual-dataset",
            "description": "some-conceptual-dataset",
            "description_de": "some-conceptual-dataset",
            "study": study_import_manager.study.id,
        }
        result = model_to_dict(
            conceptual_dataset,
            fields=(
                "name",
                "label",
                "label_de",
                "description",
                "description_de",
                "study",
            ),
        )
        assert exptected == result

    def test_import_instruments(
        self, study_import_manager, study, period, elasticsearch_indices, analysis_unit
    ):
        assert 0 == Instrument.objects.count()
        study_import_manager.import_single_entity("instruments")
        assert 1 == Instrument.objects.count()

        instrument = Instrument.objects.first()
        assert "some-instrument" == instrument.name
        assert study == instrument.study
        assert analysis_unit == instrument.analysis_unit
        assert period == instrument.period

    def test_import_questions(
        self, study_import_manager, elasticsearch_client, instrument
    ):
        assert 1 == Instrument.objects.count()
        assert 0 == Question.objects.count()
        study_import_manager.import_single_entity("questions")
        assert 1 == Question.objects.count()

        search = QuestionDocument.search().query("match_all")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert instrument.study.name == hit.study
        assert "some-question" == hit.name
        assert "some-instrument" == hit.instrument
        QuestionDocument.search().query("match_all").delete()

    def test_import_json_datasets(
        self, study_import_manager, elasticsearch_indices, study
    ):
        assert 0 == Variable.objects.count()
        study_import_manager.import_single_entity("datasets.json")
        assert 2 == Variable.objects.count()

        name = "some-variable"
        variable = Variable.objects.get(name=name)
        assert name == variable.name

        search = VariableDocument.search().query("match_all")
        assert 2 == search.count()
        VariableDocument.search().query("match_all").delete()

    def test_import_csv_datasets(
        self, study_import_manager, dataset, period, analysis_unit, conceptual_dataset
    ):
        study_import_manager.import_single_entity("datasets.csv")
        assert 1 == Dataset.objects.count()
        dataset.refresh_from_db()
        assert "some-dataset" == dataset.label
        assert "some-dataset" == dataset.description
        assert analysis_unit == dataset.analysis_unit
        assert period == dataset.period
        assert conceptual_dataset == dataset.conceptual_dataset

    def test_import_variables(self, study_import_manager, variable, concept):
        assert 1 == Variable.objects.count()
        study_import_manager.import_single_entity("variables")
        assert 2 == Variable.objects.count()
        variable.refresh_from_db()
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

    def test_import_publications(
        self, study_import_manager, elasticsearch_indices, study
    ):
        assert 0 == Publication.objects.count()
        study_import_manager.import_single_entity("publications")

        assert 1 == Publication.objects.count()
        publication = Publication.objects.first()
        assert "Some Publication" == publication.title
        assert "some-doi" == publication.doi
        assert study == publication.study
        search = PublicationDocument.search().query("match_all")
        assert 1 == search.count()
        response = search.execute()
        hit = response.hits[0]
        assert study.title() == hit.study
        assert "some-doi" == hit.doi
        assert 2018 == hit.year
        PublicationDocument.search().query("match_all").delete()

    def test_import_all(self, study_import_manager, elasticsearch_indices):
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

        assert ConceptDocument.search().query("match_all").count() == 1
        assert VariableDocument.search().query("match_all").count() == 2
        assert PublicationDocument.search().query("match_all").count() == 1
        assert QuestionDocument.search().query("match_all").count() == 1

        ConceptDocument.search().query("match_all").delete()
        VariableDocument.search().query("match_all").delete()
        PublicationDocument.search().query("match_all").delete()
        QuestionDocument.search().query("match_all").delete()

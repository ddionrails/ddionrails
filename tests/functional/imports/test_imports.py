# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-many-instance-attributes

import csv
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

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
from tests.file_factories import destroy_tmp_path, import_data_factory
from tests.functional.search_index_fixtures import set_up_index, tear_down_index
from tests.imports.management_commands.test_update import get_options
from tests.model_factories import StudyFactory


@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
class TestStudyImportManager(LiveServerTestCase):
    analysis_unit: Any
    concept: Any
    conceptual_dataset: Any
    dataset: Any
    period: Any
    question: Any
    study_import_manager: Any
    topic: Any
    variable: Any

    def setUp(self) -> None:
        self.tmp_path, self.patch_dict, self.files, self.file_content, self.study_name = (
            import_data_factory(clean_database=False)
        )
        self.study = Study.objects.get(name=self.study_name)
        self.study_import_manager = StudyImportManager(self.study)
        self.import_path_patch = patch(**self.patch_dict)
        self.import_path_patch.start()
        self.publication = Publication.objects.create(
            name="some-publication",
            title="Some Publication",
            study=self.study,
            type="book",
            year=2019,
        )
        set_up_index(self, Concept.objects.first(), "concepts")
        set_up_index(self, Publication.objects.first(), "publications")
        set_up_index(self, Question.objects.first(), "questions")
        set_up_index(self, Topic.objects.first(), "topics")
        set_up_index(self, Variable.objects.first(), "variables")
        return super().setUp()

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        destroy_tmp_path(self.tmp_path)
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
        Attachment.objects.all().delete()
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
        Attachment.objects.all().delete()
        self.assertEqual(0, Attachment.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "attachments"
        update(options)

        self.assertEqual(1, Attachment.objects.count())
        attachment = Attachment.objects.first()
        self.assertEqual(self.study, attachment.context_study)
        expected_url = self.file_content["attachments.csv"][0]["url"]
        self.assertEqual(expected_url, attachment.url)
        expected_text = self.file_content["attachments.csv"][0]["url_text"]
        self.assertEqual(expected_text, attachment.url_text)

    def test_import_concepts(self):

        options = get_options(self.study.name)
        options["entity"] = "topics.csv"
        update(options)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)

        # concepts.csv will be extended through one concept from the variables.csv
        concept_names = set(line["name"] for line in self.file_content["concepts.csv"])
        self.assertEqual(len(concept_names), Concept.objects.count())
        concept_data = self.file_content["concepts.csv"][0]
        concept = Concept.objects.get(name=concept_data["name"])
        self.assertEqual(concept_data["name"], concept.name)
        self.assertEqual(concept_data["label"], concept.label)

        set_up_index(self, Concept.objects.all(), "concepts")
        search = ConceptDocument.search().query("match_all")

        self.assertEqual(len(concept_names), search.count())
        response = search.execute()
        self.assertIn(concept_data["name"], [hit.name for hit in response.hits])

    def test_import_questions_variables(self):
        QuestionVariable.objects.all().delete()
        self.assertEqual(0, QuestionVariable.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "questions"
        update(options)
        options["entity"] = "questions_variables"
        update(options)

        question_variables_data = self.file_content["questions_variables.csv"]

        question_variables = list(QuestionVariable.objects.all())
        self.assertEqual(len(question_variables_data), len(question_variables))
        QuestionVariable.objects.get(
            variable__name=question_variables_data[0]["variable"]
        )

    def test_import_concepts_questions(self):
        ConceptQuestion.objects.all().delete()
        self.assertEqual(0, ConceptQuestion.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "concepts_questions"
        update(options)

        self.assertEqual(1, ConceptQuestion.objects.count())
        concept_data = self.file_content["concepts.csv"]
        concept_names = set(line["name"] for line in concept_data)
        question_data = self.file_content["questions.csv"]
        question_names = set(line["name"] for line in question_data)
        concept_questions = ConceptQuestion.objects.all()
        for concept_question in concept_questions:
            self.assertIn(concept_question.question.name, question_names)
            self.assertIn(concept_question.concept.name, concept_names)

    def test_import_transformations(self):
        Transformation.objects.all().delete()
        self.assertEqual(0, Transformation.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "transformations"
        update(options)

        transformation_data = self.file_content["transformations.csv"]

        self.assertEqual(len(transformation_data), Transformation.objects.count())
        for line in transformation_data:
            Transformation.objects.get(
                origin__name=line["origin_variable_name"],
                target__name=line["target_variable_name"],
            )


@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
class TestStudyImportManagerCleanDatabase(LiveServerTestCase):

    def setUp(self) -> None:
        self.tmp_path, self.patch_dict, self.files, self.file_content, self.study_name = (
            import_data_factory(clean_database=True)
        )
        self.study = StudyFactory(name=self.study_name)
        self.study_import_manager = StudyImportManager(self.study)
        self.import_path_patch = patch(**self.patch_dict)
        self.import_path_patch.start()
        self.publication = Publication.objects.create(
            name="some-publication",
            title="Some Publication",
            study=self.study,
            type="book",
            year=2019,
        )
        return super().setUp()

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        destroy_tmp_path(self.tmp_path)
        return super().tearDown()

    def test_import_study(self):  # pylint: disable=unused-argument

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "study"
        update(options)

        self.assertEqual(1, Study.objects.count())
        # refresh
        study = Study.objects.first()
        self.assertIn(study.label, self.file_content["study.md"])
        self.assertEqual({"variables": {"label-table": True}}, study.config)

    def test_import_csv_topics(self):
        topic_count = Topic.objects.count()

        self.assertEqual(0, topic_count)

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "topics.csv"
        update(options)

        topics = self.file_content["topics.csv"]

        self.assertEqual(
            len(set(topic["name"] for topic in topics)), Topic.objects.count()
        )
        first_topic = topics[0]
        topic = Topic.objects.get(name=first_topic["name"])
        parent_topic = Topic.objects.get(name=first_topic["parent"])
        self.assertEqual(first_topic["label"], topic.label)
        self.assertEqual(parent_topic, topic.parent)

    def test_import_json_topics(self):  # pylint: disable=unused-argument
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

    def test_import_analysis_units(self):
        self.assertEqual(0, AnalysisUnit.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "analysis_units"
        update(options)

        analysis_unit_data = self.file_content["analysis_units.csv"]

        self.assertEqual(len(analysis_unit_data), AnalysisUnit.objects.count())
        for line in analysis_unit_data:
            AnalysisUnit.objects.get(
                name=line["name"], label=line["label"], description=line["description"]
            )

    def test_import_periods(self):
        self.assertEqual(0, Period.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "periods"
        update(options)

        period_data = self.file_content["periods.csv"]
        self.assertEqual(len(period_data), Period.objects.count())
        for line in period_data:
            period = Period.objects.get(name=line["name"], label=line["label"])
            self.assertEqual(self.study, period.study)

    def test_import_conceptual_datasets(self):
        self.assertEqual(0, ConceptualDataset.objects.count())

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "datasets.csv"
        update(options)
        options["entity"] = "conceptual_datasets"
        update(options)

        conceptual_dataset_data = self.file_content["conceptual_datasets.csv"]

        self.assertEqual(len(conceptual_dataset_data), ConceptualDataset.objects.count())
        for line in conceptual_dataset_data:
            ConceptualDataset.objects.get(name=line["name"], label=line["label"])

    def test_import_instruments(self):
        self.assertEqual(0, Instrument.objects.count())
        self.assertEqual(0, Question.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "instruments.json"
        _, error = update(options)
        self.assertIsNone(error)

        instrument_data = self.file_content["instruments.csv"]
        instrument_name = instrument_data[0]["name"]
        question_data = self.file_content[f"{instrument_name}.json"]["questions"]

        self.assertEqual(len(instrument_data), Instrument.objects.count())
        self.assertEqual(len(question_data), Question.objects.count())
        for line in instrument_data:
            Instrument.objects.get(study=self.study, name=line["name"])

        call_command("search_index", "--populate", "--no-parallel")
        for question_name in question_data:
            search = QuestionDocument.search().query("match", name=question_name)
            self.assertTrue(search.count() > 0)
        response = search.execute()
        hit = response.hits[0]
        self.assertEqual(self.study.name, hit.study["name"])
        self.assertIn(hit.name, question_data)
        self.assertEqual(instrument_data[0]["label"], hit.instrument["label"])

    def test_import_json_datasets(self):
        self.assertEqual(0, Dataset.objects.count())
        self.assertEqual(0, Variable.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "datasets.json"
        _, error = update(options)
        self.assertIsNone(error)

        dataset_data = self.file_content["datasets.csv"]
        dataset_name = dataset_data[0]["name"]
        variable_data = self.file_content[f"{dataset_name}.json"]

        self.assertEqual(len(dataset_data), Dataset.objects.count())
        self.assertEqual(len(variable_data), Variable.objects.count())

        for dataset in dataset_data:
            dataset_object = Dataset.objects.get(name=dataset["name"])
            self.assertEqual(self.study, dataset_object.study)

        for variable in variable_data:
            Variable.objects.get_or_create(name=variable["name"])

        set_up_index(self, Variable.objects.all(), "variables")

        search = VariableDocument.search().query("match_all")
        self.assertEqual(len(variable_data), len(search.execute()))

    def test_import_csv_datasets(self):
        options = get_options(self.study.name)
        options["entity"] = "analysis_units"
        update(options)
        options["entity"] = "periods"
        update(options)
        options["entity"] = "datasets.csv"
        _, error = update(options)
        self.assertIsNone(error)

        dataset_data = self.file_content["datasets.csv"]

        periods_names = set(line["name"] for line in self.file_content["periods.csv"])
        analysis_units_names = set(
            line["name"] for line in self.file_content["analysis_units.csv"]
        )

        self.assertEqual(len(dataset_data), Dataset.objects.count())
        for line in dataset_data:
            Dataset.objects.get(
                name=line["name"],
                label=line["label"],
                period__name__in=periods_names,
                analysis_unit__name__in=analysis_units_names,
            )

    def test_import_variables(self):
        self.assertEqual(0, Variable.objects.count())

        options = get_options(self.study.name)
        options["entity"] = "topics.csv"
        _, error = update(options)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)
        options["entity"] = "datasets.csv"
        _, error = update(options)

        options["entity"] = "variables"
        _, error = update(options)
        self.assertIsNone(error)

        variable_data = self.file_content["variables.csv"]
        variable_names = set(variable["name"] for variable in variable_data)

        concept_names = set(
            concept["name"] for concept in self.file_content["concepts.csv"]
        )

        self.assertEqual(len(variable_names), Variable.objects.count())
        for line in variable_data:
            if line["concept"] != "":
                Variable.objects.get(
                    name=line["name"],
                    dataset__name=line["dataset"],
                    concept__name__in=concept_names,
                )
            else:
                Variable.objects.get(
                    name=line["name"],
                    dataset__name=line["dataset"],
                    concept=None,
                )

    def test_import_variables_empty_concept(self):
        """Do not create concept with empty, "", name."""

        options = get_options(self.study.name)
        options["entity"] = "topics.csv"
        _, error = update(options)
        options["entity"] = "concepts"
        _, error = update(options)
        self.assertIsNone(error)
        options["entity"] = "datasets.csv"
        _, error = update(options)

        options["entity"] = "variables"
        _, error = update(options)
        self.assertIsNone(error)

        variables_data = self.file_content["variables.csv"]
        variables_no_concept = [line for line in variables_data if line["concept"] == ""]
        self.assertGreater(len(variables_no_concept), 0)

        for line in variables_no_concept:
            Variable.objects.get(name=line["name"], dataset__name=line["dataset"])

        self.assertEqual(0, len(Concept.objects.filter(name="")))

    def test_import_publications(self):
        self.assertEqual(1, Publication.objects.count())
        Publication.objects.all().delete()

        options = get_options(self.study_import_manager.study.name)
        options["entity"] = "publications"
        update(options)

        self.assertEqual(1, Publication.objects.count())
        set_up_index(self, Publication.objects.all(), "publications")
        for line in self.file_content["publications.csv"]:
            publication = Publication.objects.get(doi=line["doi"])
            self.assertEqual(line["title"], publication.title)
            self.assertEqual(self.study, publication.study)
            search = PublicationDocument.search().query("match", name=line["name"])
            self.assertEqual(1, search.count())
            response = search.execute()
            hit_count = 0
            for hit in response.hits:
                if (
                    self.study.title() == hit.study_name
                    and line["doi"] == hit.doi
                    and int(line["year"]) == int(hit.year)
                ):
                    hit_count = hit_count + 1
            self.assertEqual(1, hit_count)


@override_settings(ROOT_URLCONF="tests.functional.browser.search.mock_urls")
class ImportAll(LiveServerTestCase):
    study: Study

    def setUp(self) -> None:
        self.tmp_path, self.patch_dict, self.files, self.file_content, self.study_name = (
            import_data_factory(clean_database=True)
        )

        Study.objects.all().delete()
        Concept.objects.all().delete()
        self.study = StudyFactory(name=self.study_name)
        self.import_path_patch = patch(**self.patch_dict)
        self.import_path_patch.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.import_path_patch.stop()
        destroy_tmp_path(self.tmp_path)
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

        content = self.file_content

        concept_names = set(line["name"] for line in content["concepts.csv"])
        self.assertEqual(
            len(concept_names),
            Concept.objects.count(),
        )
        self.assertEqual(
            len(content["conceptual_datasets.csv"]),
            ConceptualDataset.objects.count(),
        )
        self.assertEqual(len(content["datasets.csv"]), Dataset.objects.count())
        variable_names = set(line["name"] for line in content["variables.csv"])
        self.assertEqual(
            len(variable_names),
            Variable.objects.count(),
        )
        self.assertEqual(len(content["periods.csv"]), Period.objects.count())
        self.assertEqual(len(content["publications.csv"]), Publication.objects.count())
        question_names = set(line["name"] for line in content["questions.csv"])
        self.assertEqual(
            len(question_names),
            Question.objects.filter(instrument__study=self.study).count(),
        )
        self.assertEqual(
            len(content["transformations.csv"]), Transformation.objects.count()
        )
        self.assertEqual(len(content["instruments.csv"]), Instrument.objects.count())
        self.assertEqual(
            len(content["questions_variables.csv"]), QuestionVariable.objects.count()
        )
        self.assertEqual(
            len(content["concepts_questions.csv"]), ConceptQuestion.objects.count()
        )

        for concept in Concept.objects.all():
            concept.save()

        for concept in concept_names:
            concept_search = (
                ConceptDocument.search().query("match", name=concept).execute()
            )
            self.assertGreater(len(concept_search), 0)
        for variable in variable_names:
            variable_search = (
                VariableDocument.search().query("match", name=variable).execute()
            )
            self.assertGreater(len(variable_search), 0)
        for publication in content["publications.csv"]:
            publication_search = (
                PublicationDocument.search()
                .query("match", title=publication["title"])
                .execute()
            )
            self.assertGreater(len(publication_search), 0)

        for question in question_names:
            question_search = (
                QuestionDocument.search().query("match", name=question).execute()
            )
            self.assertGreater(len(question_search), 0)

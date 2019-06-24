# -*- coding: utf-8 -*-

""" Import functions for ddionrails project """

import json
import logging

import frontmatter
import tablib

from ddionrails.base.exceptions import DataImportError
from ddionrails.concepts.resources import (
    AnalysisUnitResource,
    ConceptResource,
    ConceptualDatasetResource,
    PeriodResource,
    TopicResource,
)
from ddionrails.data.resources import (
    DatasetResource,
    TransformationResource,
    VariableResource,
)
from ddionrails.instruments.resources import (
    ConceptQuestionResource,
    InstrumentResource,
    QuestionResource,
    QuestionVariableResource,
)
from ddionrails.publications.resources import AttachmentResource, PublicationResource
from ddionrails.studies.models import Study
from ddionrails.studies.resources import StudyResource

logging.config.fileConfig("logging.conf")
LOGGER = logging.getLogger(__name__)


def create_dataset(filename):
    dataset = tablib.Dataset().load(open(filename).read())
    # attach filename to dataset, for logging errors
    dataset.filename = filename
    return dataset


def import_dataset(resource, dataset):
    dry_run_result = resource().import_data(dataset, dry_run=True)
    if dry_run_result.totals["invalid"] > 0:
        LOGGER.error(f"{resource.__name__}: {dataset.filename.name}")

        for e in dry_run_result.base_errors:
            LOGGER.error(e)
            LOGGER.error(e.error)
            LOGGER.error(e.row)
            LOGGER.error(e.traceback)

        for row in dry_run_result.invalid_rows:
            LOGGER.error(row.error_dict)

        raise DataImportError(dry_run_result.totals)

    if not dry_run_result.has_errors():
        result = resource().import_data(dataset, dry_run=False)
        return dict(result.totals)
    else:
        # TODO
        print(dry_run_result.has_errors())
        print(dry_run_result.has_validation_errors())
        print(dry_run_result.totals)
        print(dry_run_result.row_errors())
        for e in dry_run_result.base_errors:
            print(e)
            print(e.error)
            print(e.row)
            print(e.traceback)
        for row in dry_run_result.invalid_rows:
            print(row.error_dict)
        for _, row in dry_run_result.row_errors():
            for error in row:
                print(error.error)
        raise DataImportError(dry_run_result.totals)


def import_studies(filename):
    dataset = create_dataset(filename)
    return import_dataset(StudyResource, dataset)


def import_study_description(filename, study: Study = None):
    headers = ("name", "label", "config", "doi", "description")
    with open(filename, "r") as infile:
        jekyll_content = frontmatter.load(infile)
    name = jekyll_content.metadata.get("name")
    label = jekyll_content.metadata.get("label")
    config = jekyll_content.metadata.get("config")
    doi = jekyll_content.metadata.get("doi", "")
    description = jekyll_content.content
    values = (name, label, config, doi, description)
    dataset = tablib.Dataset(values, headers=headers)
    # attach filename to dataset, for logging errors
    dataset.filename = filename
    return import_dataset(StudyResource, dataset)


def import_topics_csv(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(TopicResource, dataset)


def import_topics_json(filename, study: Study = None) -> None:
    """ TODO: Workaround """
    with open(filename, "r") as infile:
        data = json.load(infile)
    study.topic_languages = ["de", "en"]
    study.save()
    study.set_topiclist(data)


def import_concepts(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(ConceptResource, dataset)


def import_analysis_units(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(AnalysisUnitResource, dataset)


def import_conceptual_datasets(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(ConceptualDatasetResource, dataset)


def import_periods(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(PeriodResource, dataset)


def import_publications(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(PublicationResource, dataset)


def import_attachments(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(AttachmentResource, dataset)


def import_questions_variables(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(QuestionVariableResource, dataset)


def import_concepts_questions(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(ConceptQuestionResource, dataset)


def import_instruments(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(InstrumentResource, dataset)


def import_questions(filename, study: Study = None):
    with open(filename, "r") as infile:
        data = json.load(infile)
    if isinstance(data, dict) and "questions" in data:
        data = list(data["questions"].values())
    elif isinstance(data, list):
        pass
    else:
        pass
    dataset = tablib.Dataset()
    dataset.json = json.dumps(data)
    # attach filename to dataset, for logging errors
    dataset.filename = filename
    return import_dataset(QuestionResource, dataset)


def import_datasets_csv(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(DatasetResource, dataset)


def import_datasets_json(filename, study: Study = None):
    with open(filename, "r") as infile:
        data = json.load(infile)
    if isinstance(data, dict):
        data = list(data.values())
    elif isinstance(data, list):
        pass
    else:
        pass
    dataset = tablib.Dataset()
    dataset.json = json.dumps(data)
    # attach filename to dataset, for logging errors
    dataset.filename = filename
    return import_dataset(VariableResource, dataset)


def import_variables(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(VariableResource, dataset)


def import_transformations(filename, study: Study = None):
    dataset = create_dataset(filename)
    return import_dataset(TransformationResource, dataset)

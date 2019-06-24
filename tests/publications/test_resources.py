# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for ddionrails.publications.resources """

import pytest
import tablib

from ddionrails.data.models import Dataset, Variable
from ddionrails.instruments.models import Instrument, Question
from ddionrails.publications.models import Attachment, Publication
from ddionrails.publications.resources import AttachmentResource, PublicationResource
from ddionrails.studies.models import Study

pytestmark = [pytest.mark.django_db, pytest.mark.resources]


@pytest.fixture
def publication_tablib_dataset():
    """ A tablib.Dataset containing a publication """

    headers = (
        "study",
        "name",
        "title",
        "author",
        "year",
        "abstract",
        "cite",
        "sub_type",
        "url",
        "doi",
    )
    study = "some-study"
    name = "1"
    title = "Some Publication"
    author = "Surname, Firstname"
    year = 2018
    abstract = "The abstract"
    cite = "Citation"
    sub_type = "Sub type"
    url = "some-url"
    doi = "some-doi"
    values = (study, name, title, author, year, abstract, cite, sub_type, url, doi)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def study_attachment_tablib_dataset():
    """ A tablib.Dataset containing an attachment for a study """

    headers = (
        "type",
        "study",
        "dataset",
        "variable",
        "instrument",
        "question",
        "url",
        "url_text",
    )
    type_ = "study"
    study = "some-study"
    dataset = ""
    variable = ""
    instrument = ""
    question = ""
    url = "some-url"
    url_text = "some-url-text"
    values = (type_, study, dataset, variable, instrument, question, url, url_text)
    return tablib.Dataset(values, headers=headers)


@pytest.fixture
def dataset_attachment_tablib_dataset(study_attachment_tablib_dataset):
    """ A tablib.Dataset containing an attachment for a dataset """
    attachment_tablib_dataset = study_attachment_tablib_dataset
    # modify contents
    row = list(attachment_tablib_dataset.lpop())
    row[attachment_tablib_dataset.headers.index("type")] = "dataset"
    row[attachment_tablib_dataset.headers.index("dataset")] = "some-dataset"
    attachment_tablib_dataset.rpush(row)
    return attachment_tablib_dataset


@pytest.fixture
def instrument_attachment_tablib_dataset(study_attachment_tablib_dataset):
    """ A tablib.Dataset containing an attachment for an instrument """
    attachment_tablib_dataset = study_attachment_tablib_dataset
    # modify contents
    row = list(attachment_tablib_dataset.lpop())
    row[attachment_tablib_dataset.headers.index("type")] = "instrument"
    row[attachment_tablib_dataset.headers.index("instrument")] = "some-instrument"
    attachment_tablib_dataset.rpush(row)
    return attachment_tablib_dataset


@pytest.fixture
def variable_attachment_tablib_dataset(dataset_attachment_tablib_dataset):
    """ A tablib.Dataset containing an attachment for a variable """
    attachment_tablib_dataset = dataset_attachment_tablib_dataset
    # modify contents
    row = list(attachment_tablib_dataset.lpop())
    row[attachment_tablib_dataset.headers.index("type")] = "variable"
    row[attachment_tablib_dataset.headers.index("variable")] = "some-variable"
    attachment_tablib_dataset.rpush(row)
    return attachment_tablib_dataset


@pytest.fixture
def question_attachment_tablib_dataset(study_attachment_tablib_dataset):
    """ A tablib.Dataset containing an attachment for a question """
    attachment_tablib_dataset = study_attachment_tablib_dataset
    # modify contents
    row = list(attachment_tablib_dataset.lpop())
    row[attachment_tablib_dataset.headers.index("type")] = "question"
    row[attachment_tablib_dataset.headers.index("instrument")] = "some-instrument"
    row[attachment_tablib_dataset.headers.index("question")] = "some-question"
    attachment_tablib_dataset.rpush(row)
    return attachment_tablib_dataset


class TestPublicationResource:
    def test_resource_import_succeeds(self, study, publication_tablib_dataset):
        assert 0 == Publication.objects.count()
        result = PublicationResource().import_data(publication_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Publication.objects.count()

        publication = Publication.objects.first()

        # test attributes
        name = publication_tablib_dataset["name"][0]
        title = publication_tablib_dataset["title"][0]
        author = publication_tablib_dataset["author"][0]
        abstract = publication_tablib_dataset["abstract"][0]
        cite = publication_tablib_dataset["cite"][0]
        sub_type = publication_tablib_dataset["sub_type"][0]
        url = publication_tablib_dataset["url"][0]
        doi = publication_tablib_dataset["doi"][0]

        assert name == publication.name
        assert title == publication.title
        assert author == publication.author
        assert abstract == publication.abstract
        assert cite == publication.cite
        assert sub_type == publication.sub_type
        assert url == publication.url
        assert doi == publication.doi

        # test relations
        assert study == publication.study


class TestAttachmentResource:
    def test_resource_import_study_attachment_succeeds(
        self, study, study_attachment_tablib_dataset
    ):
        assert 1 == Study.objects.count()
        assert 0 == Attachment.objects.count()
        result = AttachmentResource().import_data(study_attachment_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()

        # test attributes
        url = study_attachment_tablib_dataset["url"][0]
        url_text = study_attachment_tablib_dataset["url_text"][0]
        assert url == attachment.url
        assert url_text == attachment.url_text

        # test relations
        assert study == attachment.study
        assert study == attachment.context_study

    def test_resource_import_dataset_attachment_succeeds(
        self, dataset, dataset_attachment_tablib_dataset
    ):
        assert 1 == Dataset.objects.count()
        assert 0 == Attachment.objects.count()
        result = AttachmentResource().import_data(dataset_attachment_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()

        # test relations
        assert dataset == attachment.dataset
        assert dataset.study == attachment.context_study

    def test_resource_import_instrument_attachment_succeeds(
        self, instrument, instrument_attachment_tablib_dataset
    ):
        assert 1 == Instrument.objects.count()
        assert 0 == Attachment.objects.count()
        result = AttachmentResource().import_data(instrument_attachment_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()

        # test relations
        assert instrument == attachment.instrument
        assert instrument.study == attachment.context_study

    def test_resource_import_variable_attachment_succeeds(
        self, variable, variable_attachment_tablib_dataset
    ):
        assert 1 == Variable.objects.count()
        assert 0 == Attachment.objects.count()
        result = AttachmentResource().import_data(variable_attachment_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()

        # test relations
        assert variable == attachment.variable
        assert variable.dataset.study == attachment.context_study

    def test_resource_import_question_attachment_succeeds(
        self, question, question_attachment_tablib_dataset
    ):
        assert 1 == Question.objects.count()
        assert 0 == Attachment.objects.count()
        result = AttachmentResource().import_data(question_attachment_tablib_dataset)
        assert False is result.has_errors()
        assert 1 == Attachment.objects.count()
        attachment = Attachment.objects.first()

        # test relations
        assert question == attachment.question
        assert question.instrument.study == attachment.context_study

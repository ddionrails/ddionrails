# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.concepts app """

import pytest
from django.forms.models import model_to_dict

from ddionrails.concepts.documents import ConceptDocument, TopicDocument

pytestmark = [
    pytest.mark.search,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]


def test_concept_search_document_fields(
    concepts_index, variable_with_concept  # pylint: disable=unused-argument
):
    variable = variable_with_concept
    concept = variable.concept
    concept.save()

    search = ConceptDocument.search().query("match_all")

    expected = 1
    assert expected == search.count()

    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(concept.id) == document.meta.id
    assert "testing_concepts" == document.meta.index

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        concept, fields=("name", "label", "label_de", "description", "description_de")
    )
    # add relations to expected dictionary
    expected["study"] = [variable.dataset.study.name]
    expected["type"] = "concept"
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result


def test_search_concept_by_label_de(concepts_index):  # pylint: disable=unused-argument
    result = ConceptDocument.search().query("match", label_de="Konzept").count()
    expected = 1
    assert expected == result


def test_topic_search_document_fields(
    topics_index, topic  # pylint: disable=unused-argument
):
    search = TopicDocument.search().query("match_all")
    expected = 1
    assert expected == search.count()

    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(topic.id) == document.meta.id
    assert "testing_topics" == document.meta.index

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        topic, fields=("name", "label", "label_de", "description", "description_de")
    )
    # add relations to expected dictionary
    expected["study"] = topic.study.title()
    expected["type"] = "topic"
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result


def test_concept_search_document_study_by_topic(
    concepts_index, concept, topic  # pylint: disable=unused-argument
):
    """ Test this relation:
        study <-> topic <-> concept
    """
    concept.topics.add(topic)
    concept.save()
    response = ConceptDocument.search().execute()
    document = response.hits[0]
    assert [topic.study.title()] == document.study


def test_concept_search_document_study_by_variable(
    concepts_index, variable_with_concept  # pylint: disable=unused-argument
):
    """ Test this relation:
        study <-> dataset <-> variable <-> concept
    """
    variable_with_concept.concept.save()
    response = ConceptDocument.search().execute()
    document = response.hits[0]
    assert [variable_with_concept.dataset.study.title()] == document.study


def test_concept_search_document_study_by_question(
    concepts_index, concept_question  # pylint: disable=unused-argument
):
    """ Test this relation:
        study <-> instrument <-> question <-> concept
    """
    concept_question.concept.save()
    response = ConceptDocument.search().execute()
    document = response.hits[0]
    assert [concept_question.question.instrument.study.title()] == document.study


def test_concept_search_document_study_by_all(
    concepts_index,  # pylint: disable=unused-argument
    concept_question,
    variable_with_concept,  # pylint: disable=unused-argument
    topic,
):
    concept_question.concept.topics.add(topic)
    concept_question.concept.save()
    response = ConceptDocument.search().execute()
    document = response.hits[0]
    assert [concept_question.question.instrument.study.title()] == document.study

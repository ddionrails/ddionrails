# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for documents in ddionrails.concepts app """

from typing import Any

import pytest
from django.forms.models import model_to_dict

from ddionrails.concepts.documents import ConceptDocument, TopicDocument

pytestmark = [
    pytest.mark.search,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]


@pytest.mark.usefixtures("concepts_index")
def test_concept_search_document_fields(variable_with_concept, topic):
    variable = variable_with_concept
    concept = variable.concept
    concept.topics.add(topic)
    concept.save()

    search = ConceptDocument.search().query("match_all")

    expected_count = 1
    assert expected_count == search.count()

    response = search.execute()
    document = response.hits[0]

    # test meta
    assert str(concept.id) == document.meta.id
    assert "testing_concepts" == document.meta.index

    # generate expected dictionary with attributes from model instance
    expected = model_to_dict(
        instance=concept,
        fields=("name", "label", "label_de", "description", "description_de"),
    )
    # add relations to expected dictionary
    expected["study_name"] = [variable.dataset.study.label]
    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result


@pytest.mark.usefixtures("concepts_index")
def test_search_concept_by_label_de():
    result = ConceptDocument.search().query("match", label_de="Konzept").count()
    expected = 1
    assert expected == result


@pytest.mark.usefixtures("topics_index")
@pytest.mark.django_db
def test_topic_search_document_fields(topic):
    search = TopicDocument.search().query("match_all")
    expected: Any = 1
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
    expected["study_name"] = topic.study.title()
    expected["id"] = str(topic.id)
    expected["study"] = {
        "name": topic.study.name,
        "label": topic.study.label,
    }

    # generate result dictionary from search document
    result = document.to_dict()
    assert expected == result

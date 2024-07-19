# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

""" Test cases for models in ddionrails.concepts app """

import pytest

from ddionrails.concepts.models import Topic

from .factories import TopicFactory

pytestmark = [pytest.mark.concepts, pytest.mark.models]


class TestConceptModel:
    def test_string_method(self, concept):  # pylint: disable=unused-argument
        assert str(concept) == "/concept/" + concept.name

    def test_get_absolute_url_method(self, concept):
        assert concept.get_absolute_url() == "/concept/" + str(concept.id)


class TestAnalysisUnitModel:
    def test_string_method(self, analysis_unit):
        assert str(analysis_unit) == "/analysis_unit/" + analysis_unit.name


class TestConceptualDatasetModel:
    def test_string_method(self, conceptual_dataset):
        assert str(conceptual_dataset) == "/conceptual_dataset/" + conceptual_dataset.name


class TestPeriodModel:
    def test_string_method(self, period):
        assert str(period) == "/period/" + period.name


@pytest.mark.django_db
class TestTopicModel:
    def test_get_children_method(self, topic):
        child_topic = TopicFactory(name="child-topic", parent=topic)
        grand_child_topic = TopicFactory(name="grand-child-topic", parent=child_topic)
        children = Topic.get_children(topic.pk)
        assert child_topic in children
        assert grand_child_topic in children

    def test_get_topic_tree_leafs(self, topic, concept):
        child_topic = TopicFactory(name="child-topic", parent=topic)
        grand_child_topic = TopicFactory(name="grand-child-topic", parent=child_topic)
        grand_grand_child_topic = TopicFactory(
            name="grand-grand-child-topic", parent=grand_child_topic
        )
        grand_grand_child_topic.concepts.add(concept)
        grand_grand_child_topic.save()
        other_grand_child_topic = TopicFactory(
            name="other-grand-grand-child-topic", parent=child_topic
        )
        other_grand_child_topic.concepts.add(concept)
        other_grand_child_topic.save()

        children = topic.get_topic_tree_leafs()
        assert child_topic not in children
        assert grand_child_topic not in children
        assert grand_grand_child_topic in children
        assert other_grand_child_topic in children

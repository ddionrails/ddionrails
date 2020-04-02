# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for models in ddionrails.concepts app """

import pytest

from ddionrails.concepts.models import Topic

from .factories import TopicFactory

pytestmark = [pytest.mark.concepts, pytest.mark.models]


class TestConceptModel:
    def test_string_method(self, concept):  # pylint: disable=unused-argument
        assert str(concept) == "/concept/" + concept.name

    def test_get_absolute_url_method(self, concept):
        assert concept.get_absolute_url() == "/concept/" + concept.name


class TestAnalysisUnitModel:
    def test_string_method(self, analysis_unit):
        assert str(analysis_unit) == "/analysis_unit/" + analysis_unit.name


class TestConceptualDatasetModel:
    def test_string_method(self, conceptual_dataset):
        assert str(conceptual_dataset) == "/conceptual_dataset/" + conceptual_dataset.name


class TestPeriodModel:
    def test_string_method(self, period):
        assert str(period) == "/period/" + period.name


class TestTopicModel:
    def test_get_children_method(self, topic):
        child_topic = TopicFactory(name="child-topic", parent=topic)
        grand_child_topic = TopicFactory(name="grand-child-topic", parent=child_topic)
        children = Topic.get_children(topic.pk)
        assert child_topic in children
        assert grand_child_topic in children

    def test_get_topic_tree_leaves(self, topic):
        child_topic = TopicFactory(name="child-topic", parent=topic)
        grand_child_topic = TopicFactory(name="grand-child-topic", parent=child_topic)
        children = Topic.get_topic_tree_leaves(topic_id=topic.pk)
        assert child_topic not in children
        assert grand_child_topic in children

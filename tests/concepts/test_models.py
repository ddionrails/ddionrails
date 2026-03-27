# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name

"""Test cases for models in ddionrails.concepts app"""

from django.test import TestCase

from ddionrails.concepts.models import Topic
from tests.model_factories import (
    AnalysisUnitFactory,
    ConceptFactory,
    ConceptualDatasetFactory,
    PeriodFactory,
    TopicFactory,
)


class TestConceptModel(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.concept = ConceptFactory()
        return super().setUpClass()

    def test_string_method(self):  # pylint: disable=unused-argument
        self.assertEqual(str(self.concept), "/concept/" + self.concept.name)

    def test_get_absolute_url_method(self):
        self.assertEqual(
            self.concept.get_absolute_url(), "/concept/" + str(self.concept.id)
        )


class TestAnalysisUnitModel(TestCase):
    def test_string_method(self):
        analysis_unit = AnalysisUnitFactory()
        self.assertEqual(str(analysis_unit), "/analysis_unit/" + analysis_unit.name)


class TestConceptualDatasetModel(TestCase):
    def test_string_method(self):
        conceptual_dataset = ConceptualDatasetFactory()
        self.assertEqual(
            str(conceptual_dataset), "/conceptual_dataset/" + conceptual_dataset.name
        )


class TestPeriodModel(TestCase):
    def test_string_method(self):
        period = PeriodFactory()
        self.assertEqual(str(period), "/period/" + period.name)


class TestTopicModel(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.topic = TopicFactory(parent__depth=4)
        cls.topic_parent = cls.topic.parent
        cls.sibling_topic = TopicFactory(study=cls.topic.study, parent=cls.topic.parent)
        cls.topic_grand_parent = cls.topic_parent.parent
        cls.concept = ConceptFactory(topics=[cls.topic, cls.sibling_topic])
        return super().setUpClass()

    def test_get_children_method(self):
        topic = self.topic_grand_parent
        child_topic = self.topic_parent
        grand_child_topic = self.topic
        children = Topic.get_children(topic.pk)
        assert child_topic in children
        assert grand_child_topic in children

    def test_get_topic_tree_leafs(self):

        children = self.topic_grand_parent.get_topic_tree_leafs()
        assert self.topic_grand_parent not in children
        assert self.topic_parent not in children
        assert self.topic in children
        assert self.sibling_topic in children

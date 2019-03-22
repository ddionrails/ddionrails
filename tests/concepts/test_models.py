import pytest

from concepts.models import Concept, Topic
from elastic.mixins import ModelMixin

from .factories import TopicFactory

pytestmark = [pytest.mark.concepts, pytest.mark.models]


class TestConceptModel:
    def test_string_method(self, concept):
        assert str(concept) == "/concept/" + concept.name

    def test_get_absolute_url_method(self, concept):
        assert concept.get_absolute_url() == "/concept/" + concept.name

    def test_index_method_with_concept_with_label(self, mocker, concept):
        mocker.patch("elastic.mixins.ModelMixin.set_elastic")
        concept.index()
        ModelMixin.set_elastic.assert_called_once()

    def test_index_method_with_concept_without_label(self, mocker, concept_without_label):
        mocker.patch("elastic.mixins.ModelMixin.set_elastic")
        concept_without_label.index()
        ModelMixin.set_elastic.assert_called_once()

    # TODO: what happens at index_all() without concepts in database
    def test_index_all_method_with_no_concepts(self, db):
        Concept.index_all()

    def test_index_all_method_with_one_concept(self, mocker, concept):
        mocker.patch("concepts.models.Concept.index")
        Concept.index_all()
        Concept.index.assert_called_once()


class TestAnalysisUnitModel:
    def test_string_method(self, analysis_unit):
        assert str(analysis_unit) == "/analysis_unit/" + analysis_unit.name

    def test_title_method_with_label(self, analysis_unit):
        assert analysis_unit.title() == analysis_unit.label

    def test_title_method_without_label(self, analysis_unit_without_label):
        assert analysis_unit_without_label.title() == analysis_unit_without_label.name


class TestConceptualDatasetModel:
    def test_string_method(self, conceptual_dataset):
        assert str(conceptual_dataset) == "/conceptual_dataset/" + conceptual_dataset.name

    def test_title_method_with_label(self, conceptual_dataset):
        assert conceptual_dataset.title() == conceptual_dataset.label

    def test_title_method_without_label(self, conceptual_dataset_without_label):
        assert (
            conceptual_dataset_without_label.title()
            == conceptual_dataset_without_label.name
        )


class TestPeriodModel:
    def test_string_method(self, period):
        assert str(period) == "/period/" + period.name

    def test_title_method_with_label(self, period):
        assert period.title() == period.label

    def test_title_method_without_label(self, period_without_label):
        assert period_without_label.title() == period_without_label.name

    def test_is_range_method_with_range(self, period_with_range_definition):
        assert period_with_range_definition.is_range() is True

    def test_is_range_method_without_range(self, period):
        assert period.is_range() is False


class TestTopicModel:
    def test_get_children_method(self, topic):
        child_topic = TopicFactory(name="child-topic", parent=topic)
        grand_child_topic = TopicFactory(name="grand-child-topic", parent=child_topic)
        children = Topic.get_children(topic.pk)
        assert child_topic in children
        assert grand_child_topic in children

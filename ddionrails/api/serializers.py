"""All serializers for the djangorestframework API.

Serializers are used to serialize django ORM objects to standard data formats.
"""

from typing import Any

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from rest_framework import serializers

from ddionrails.api.related_fields import BasketRelatedField, UserRelatedField
from ddionrails.data.models.dataset import Dataset
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.models.instrument import Instrument
from ddionrails.instruments.models.question import Question
from ddionrails.publications.models import Attachment
from ddionrails.studies.models import Study
from ddionrails.workspace.models.basket import Basket
from ddionrails.workspace.models.basket_variable import BasketVariable

NAMESPACE = "api"


class AttachmentSerializer(serializers.ModelSerializer):
    """Serialize a single Attachment."""

    class Meta:
        model = Attachment
        fields = ["url", "url_text"]


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize system users."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class BasketHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize the data about Baskets."""

    user = serializers.HyperlinkedRelatedField(
        view_name=NAMESPACE + ":user-detail", read_only=True
    )
    user_id = UserRelatedField()
    study = serializers.HyperlinkedRelatedField(
        view_name=NAMESPACE + ":study-detail", read_only=True
    )
    study_id = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Study.objects.all()
    )

    class Meta:
        model = Basket
        fields = [
            "id",
            "user_id",
            "name",
            "label",
            "description",
            "user",
            "study",
            "study_id",
        ]


class BasketVariableSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize a relationship between a Basket and a Variable."""

    id = serializers.HyperlinkedRelatedField(
        view_name=NAMESPACE + ":basket-variables-detail", read_only=True
    )
    basket = BasketRelatedField()
    basket_id = serializers.SlugRelatedField(
        source="basket", read_only=True, slug_field="id"
    )
    variable = serializers.HyperlinkedRelatedField(
        style={"base_template": "input.html"},
        view_name=NAMESPACE + ":variable-detail",
        queryset=Variable.objects.all(),
        read_only=False,
    )
    variable_id = serializers.SlugRelatedField(
        source="variable", read_only=True, slug_field="id"
    )

    class Meta:
        model = BasketVariable
        fields = ["id", "basket", "basket_id", "variable", "variable_id"]


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize Datasets."""

    conceptual_dataset_label = serializers.SlugRelatedField(
        source="conceptual_dataset", read_only=True, slug_field="label"
    )
    conceptual_dataset_label_de = serializers.SlugRelatedField(
        source="conceptual_dataset", read_only=True, slug_field="label_de"
    )
    period_name = serializers.SlugRelatedField(
        source="period", read_only=True, slug_field="name"
    )
    period_label = serializers.SlugRelatedField(
        source="period", read_only=True, slug_field="label"
    )
    analysis_unit_label = serializers.SlugRelatedField(
        source="analysis_unit", read_only=True, slug_field="label"
    )
    analysis_unit_label_de = serializers.SlugRelatedField(
        source="analysis_unit", read_only=True, slug_field="label_de"
    )
    study = serializers.PrimaryKeyRelatedField(read_only=True)
    study_name = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="name"
    )
    study_label = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="label"
    )
    study_label_de = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="label_de"
    )
    attachments = AttachmentSerializer(read_only=True, many=True)
    primary_key = serializers.JSONField(read_only=True)

    class Meta:
        model = Dataset
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "conceptual_dataset_label",
            "conceptual_dataset_label_de",
            "period_name",
            "period_label",
            "primary_key",
            "folder",
            "analysis_unit_label",
            "analysis_unit_label_de",
            "study",
            "study_name",
            "study_label",
            "study_label_de",
            "attachments",
        ]


class InstrumentSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize Instruments."""

    analysis_unit_name = serializers.SlugRelatedField(
        source="analysis_unit", read_only=True, slug_field="name"
    )
    period_name = serializers.SlugRelatedField(
        source="period", read_only=True, slug_field="name"
    )
    period_label = serializers.SlugRelatedField(
        source="period", read_only=True, slug_field="label"
    )
    study = serializers.PrimaryKeyRelatedField(read_only=True)
    study_name = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="name"
    )
    study_label = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="label"
    )
    study_label_de = serializers.SlugRelatedField(
        source="study", read_only=True, slug_field="label_de"
    )
    has_questions = serializers.BooleanField()
    type = serializers.JSONField()
    attachments = AttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Instrument
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "analysis_unit_name",
            "period_name",
            "period_label",
            "study",
            "study_name",
            "study_label",
            "study_label_de",
            "has_questions",
            "type",
            "mode",
            "attachments",
        ]


class _subsetDict(serializers.DictField):
    def to_representation(self, value: dict[Any, Any]) -> dict[Any, Any]:
        value = super().to_representation(value)
        return {
            "labels": value.get("labels", []),
            "labels_de": value.get("labels_de", []),
            "values": value.get("values"),
        }


class VariableLabelsSerializer(serializers.ModelSerializer):
    """Serialize labels of Variables related by concept."""

    variable = serializers.CharField(source="name")
    dataset = serializers.SlugRelatedField(read_only=True, slug_field="name")
    labels = _subsetDict(source="categories")
    period = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Variable
        fields = ["variable", "dataset", "period", "labels"]


class VariableSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize systems Variables."""

    dataset = serializers.PrimaryKeyRelatedField(read_only=True)
    dataset_name = serializers.SlugRelatedField(
        source="dataset", read_only=True, slug_field="name"
    )
    study = serializers.SlugRelatedField(
        source="dataset.study", read_only=True, slug_field="id"
    )
    study_name = serializers.SlugRelatedField(
        source="dataset.study", read_only=True, slug_field="name"
    )
    study_label = serializers.SlugRelatedField(
        source="dataset.study", read_only=True, slug_field="label"
    )
    position = serializers.IntegerField(source="sort_id")

    class Meta:
        model = Variable
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "dataset_name",
            "study_name",
            "study_label",
            "dataset",
            "study",
            "position",
        ]


class RelatedVariableSerializer(VariableSerializer):

    relation = serializers.StringRelatedField()
    study = None
    study_label = None
    study_name = None

    period_name = serializers.StringRelatedField(source="period__name", read_only=True)
    dataset_name = serializers.StringRelatedField(source="dataset__name", read_only=True)
    dataset = serializers.StringRelatedField(source="dataset_id", read_only=True)

    class Meta:
        model = Variable
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "dataset_name",
            "dataset",
            "relation",
            "period_name",
        ]


class StatisticsVariableSerializer(VariableSerializer):
    """Expand VariableSerializer with fields needed for statistics functions."""

    topics = serializers.SlugRelatedField(
        source="concept.topics", read_only=True, slug_field="label", many=True
    )
    topics_de = serializers.SlugRelatedField(
        source="concept.topics", read_only=True, slug_field="label_de", many=True
    )

    class Meta:
        model = Variable
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "dataset_name",
            "study_name",
            "study_label",
            "dataset",
            "study",
            "statistics_type",
            "topics",
            "topics_de",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize systems Variables."""

    instrument = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Instrument.objects.all()
    )
    instrument_name = serializers.SlugRelatedField(
        source="instrument", read_only=True, slug_field="name"
    )
    study = serializers.SlugRelatedField(
        source="instrument.study", read_only=True, slug_field="id"
    )
    study_name = serializers.SlugRelatedField(
        source="instrument.study", read_only=True, slug_field="name"
    )
    study_label = serializers.SlugRelatedField(
        source="instrument.study", read_only=True, slug_field="label"
    )
    position = serializers.IntegerField(source="sort_id")

    class Meta:
        model = Question
        fields = [
            "id",
            "name",
            "label",
            "label_de",
            "instrument_name",
            "study_name",
            "study_label",
            "instrument",
            "study",
            "position",
        ]


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """Serialize systems Studies."""

    class Meta:
        model = Study
        fields = ["name", "label"]

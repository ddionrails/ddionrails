"""All serializers for the djangorestframework API.

Serializers are used to serialize django ORM objects to standard data formats.
"""
from django.contrib.auth.models import User
from rest_framework import serializers

from ddionrails.api.related_fields import BasketRelatedField, UserRelatedField
from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable

NAMESPACE = "api"


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
        fields = ["user_id", "name", "label", "description", "user", "study", "study_id"]


class BasketVariableSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize a relationship between a Basket and a Variable."""

    variable = serializers.HyperlinkedRelatedField(
        style={"base_template": "input.html"},
        view_name=NAMESPACE + ":variable-detail",
        queryset=Variable.objects.all(),
        read_only=False,
    )
    basket = BasketRelatedField()

    class Meta:
        model = BasketVariable
        fields = ["basket", "variable"]


class VariableSerializer(serializers.HyperlinkedModelSerializer):
    """Serialize systems Variables."""

    class Meta:
        model = Variable
        fields = ["id", "name", "label"]


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """Serialize systems Studies."""

    class Meta:
        model = Study
        fields = ["name", "label"]

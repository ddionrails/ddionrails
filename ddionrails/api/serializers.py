from django.contrib.auth.models import User
from rest_framework import serializers

from ddionrails.api.related_fields import (
    BasketRelatedField,
    UserRelatedField,
    VariableRelatedField,
)
from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class BasketHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name="api:user-detail", read_only=True
    )
    user_id = UserRelatedField()
    study = serializers.HyperlinkedRelatedField(
        view_name="api:study-detail", read_only=True
    )
    study_id = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Study.objects.all()
    )

    class Meta:
        model = Basket
        fields = ["user_id", "name", "label", "description", "user", "study", "study_id"]


class BasketVariableSerializer(serializers.HyperlinkedModelSerializer):
    variable = VariableRelatedField(style={"base_template": "input.html"})
    basket = BasketRelatedField()

    class Meta:
        model = BasketVariable
        fields = ["basket", "variable"]


class VariableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Variable
        fields = ["pk", "name", "label"]


class StudySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Study
        fields = ["name", "label"]

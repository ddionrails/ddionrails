from django.contrib.auth.models import User
from rest_framework import serializers

from ddionrails.api.related_fields import SessionUserRelatedField, VariableRelatedField
from ddionrails.data.models.variable import Variable
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class BasketSerializer(serializers.HyperlinkedModelSerializer):
    user = SessionUserRelatedField()
    study = serializers.HyperlinkedRelatedField(
        view_name="api:study-detail", read_only=False, queryset=Study.objects.all()
    )

    class Meta:
        model = Basket
        fields = ["name", "label", "description", "user", "study"]


class BasketVariableSerializer(serializers.HyperlinkedModelSerializer):
    variable = VariableRelatedField()

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

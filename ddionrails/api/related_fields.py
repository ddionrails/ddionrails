from django.contrib.auth.models import User
from rest_framework import serializers

from ddionrails.data.models.variable import Variable
from ddionrails.workspace.models import Basket


class SessionUserRelatedField(serializers.HyperlinkedRelatedField):
    view_name = "api:user-detail"
    read_only = False

    def get_queryset(self):
        user = self.context["request"].user
        if user.is_superuser:
            return User.objects.all()
        return [User.objects.get(pk=user.id)]


class UserRelatedField(serializers.PrimaryKeyRelatedField):
    view_name = "api:user-detail"
    read_only = False

    def get_queryset(self):
        user = self.context["request"].user
        if user.is_superuser:
            return User.objects.all()
        return [User.objects.get(pk=user.id)]


class VariableRelatedField(serializers.HyperlinkedRelatedField):
    view_name = "api:variable-detail"
    read_only = False

    def get_queryset(self):
        return Variable.objects.all()


class BasketRelatedField(serializers.HyperlinkedRelatedField):
    view_name = "api:basket-detail"
    read_only = False
    queryset = Basket.objects.all()

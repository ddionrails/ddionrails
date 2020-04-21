"""Define related fields for the API."""
from django.contrib.auth.models import User
from rest_framework import serializers

from ddionrails.workspace.models import Basket


class UserRelatedField(serializers.PrimaryKeyRelatedField):
    """Point to a related User entity.

    Non privileged users can only access themselves whereas
    superusers can access all Users.
    """

    view_name = "api:user-detail"
    read_only = False

    def get_queryset(self):
        user = self.context["request"].user
        if user.is_superuser:
            return User.objects.all()
        return [User.objects.get(pk=user.id)]


class BasketRelatedField(serializers.HyperlinkedRelatedField):
    """Point to a related Basket entity."""

    view_name = "api:basket-detail"
    read_only = False
    queryset = Basket.objects.all()

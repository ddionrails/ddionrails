# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for user model """

import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = "knut"
    password = factory.PostGenerationMethodCall("set_password", "secret-password")

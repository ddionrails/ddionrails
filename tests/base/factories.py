# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.base app """

import factory

from ddionrails.base.models import System


class SystemFactory(factory.django.DjangoModelFactory):
    """System factory"""

    class Meta:
        model = System

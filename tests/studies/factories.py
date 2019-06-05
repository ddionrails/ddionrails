# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.studies app """

import factory

from ddionrails.studies.models import Study, TopicList


class StudyFactory(factory.django.DjangoModelFactory):
    """Study factory"""

    class Meta:
        model = Study
        django_get_or_create = ("name",)


class TopicListFactory(factory.django.DjangoModelFactory):
    """TopicList factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = TopicList
        django_get_or_create = ("study", "topiclist")

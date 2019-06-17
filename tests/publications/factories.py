# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" DjangoModelFactories for models in ddionrails.publications app """

import factory

from ddionrails.publications.models import Attachment, Publication
from tests.studies.factories import StudyFactory


class PublicationFactory(factory.django.DjangoModelFactory):
    """Publication factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Publication
        django_get_or_create = ("name",)


class AttachmentFactory(factory.django.DjangoModelFactory):
    """Attachment factory"""

    context_study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Attachment

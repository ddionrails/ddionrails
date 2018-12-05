import factory

from publications.models import Publication
from tests.studies.factories import StudyFactory


class PublicationFactory(factory.django.DjangoModelFactory):
    """Publication factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Publication
        django_get_or_create = ("name",)

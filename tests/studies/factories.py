import factory

from ddionrails.studies.models import Study


class StudyFactory(factory.django.DjangoModelFactory):
    """Study factory"""

    class Meta:
        model = Study
        django_get_or_create = ("name",)

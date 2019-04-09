import factory

from ddionrails.data.models import Dataset, Transformation, Variable
from tests.studies.factories import StudyFactory


class DatasetFactory(factory.django.DjangoModelFactory):
    """Dataset factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Dataset
        django_get_or_create = ("study", "name")


class TransformationFactory(factory.django.DjangoModelFactory):
    """Transformation factory"""

    class Meta:
        model = Transformation
        django_get_or_create = ("name",)


class VariableFactory(factory.django.DjangoModelFactory):
    """Variable factory"""

    dataset = factory.SubFactory(DatasetFactory, name="some-dataset")

    class Meta:
        model = Variable
        django_get_or_create = ("dataset", "name")

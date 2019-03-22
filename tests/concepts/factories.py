import factory

from concepts.models import AnalysisUnit, Concept, ConceptualDataset, Period, Topic
from tests.studies.factories import StudyFactory


class ConceptFactory(factory.django.DjangoModelFactory):
    """Concept factory"""

    class Meta:
        model = Concept
        django_get_or_create = ("name",)


class AnalysisUnitFactory(factory.django.DjangoModelFactory):
    """Analysis Unit factory"""

    class Meta:
        model = AnalysisUnit
        django_get_or_create = ("name",)


class ConceptualDatasetFactory(factory.django.DjangoModelFactory):
    """Conceptual Dataset factory"""

    class Meta:
        model = ConceptualDataset
        django_get_or_create = ("name",)


class PeriodFactory(factory.django.DjangoModelFactory):
    """Period factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Period
        django_get_or_create = ("study", "name")


class TopicFactory(factory.django.DjangoModelFactory):
    """Topic factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")

    class Meta:
        model = Topic
        django_get_or_create = ("study", "name")

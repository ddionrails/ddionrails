import factory

from instruments.models import (
    Instrument,
    Question,
)
from tests.studies.factories import StudyFactory


class InstrumentFactory(factory.django.DjangoModelFactory):
    """Instrument factory"""

    study = factory.SubFactory(StudyFactory, name='some-study')

    class Meta:
        model = Instrument
        django_get_or_create = ('study', 'name',)


class QuestionFactory(factory.django.DjangoModelFactory):
    """Question factory"""

    instrument = factory.SubFactory(InstrumentFactory, name='some-instrument')

    class Meta:
        model = Question
        django_get_or_create = ('instrument', 'name',)

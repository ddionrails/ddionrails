from django.test import TestCase

from ddionrails.studies.models import Study
from tests.factories import StudyFactory


class FactoryTest(TestCase):

    def test_study(self):
        factory = StudyFactory()
        Study.objects.get(name=factory.name)

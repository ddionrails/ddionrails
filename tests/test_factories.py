from django.test import TestCase

from ddionrails.studies.models import Study
from tests.model_factories import (
    AdminUserFactory,
    QuestionFactory,
    StudyFactory,
    TransformationFactory,
    VariableFactory,
)


class FactoryTest(TestCase):

    def test_admin_user(self):
        factory = AdminUserFactory(password="aa")

    def test_study(self):
        factory = StudyFactory()
        Study.objects.get(name=factory.name)

    def test_transformation(self):
        factory = TransformationFactory()
        factory_two = TransformationFactory(origin=factory.origin)

    def test_variable(self):
        factory = VariableFactory()
        factory_two = VariableFactory()

    def test_question(self):
        factory = QuestionFactory()
        factory_two = QuestionFactory()

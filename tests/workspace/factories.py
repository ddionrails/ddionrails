import factory

from ddionrails.workspace.models import Basket, Script
from tests.factories import UserFactory
from tests.studies.factories import StudyFactory


class BasketFactory(factory.django.DjangoModelFactory):
    """Basket factory"""

    study = factory.SubFactory(StudyFactory, name="some-study")
    user = factory.SubFactory(UserFactory, username="some-user")

    class Meta:
        model = Basket
        django_get_or_create = ("name",)


class ScriptFactory(factory.django.DjangoModelFactory):
    """Script factory"""

    basket = factory.SubFactory(BasketFactory, name="some-basket")

    class Meta:
        model = Script
        django_get_or_create = ("name",)

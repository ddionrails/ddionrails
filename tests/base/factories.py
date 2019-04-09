import factory

from ddionrails.base.models import System


class SystemFactory(factory.django.DjangoModelFactory):
    """System factory"""

    class Meta:
        model = System

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from members.factories import MemberFactory

from cmr_layouts.models import Locomotive, RollingStock


class LocomotiveFactory(DjangoModelFactory):
    class Meta:
        model = Locomotive

    name = Faker('name')


class RollingStockFactory(DjangoModelFactory):
    class Meta:
        model = RollingStock

    author = SubFactory(MemberFactory)
    title = Faker('sentence')

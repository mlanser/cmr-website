from factory import Faker
from factory.django import DjangoModelFactory

from base.models import Person


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    street = Faker('street_address')
    city = Faker('city')
    state = Faker('state')
    zip = Faker('postcode')
    email = Faker('ascii_safe_email')
    # image = Faker('image_url', width=None, height=None, category=None, randomize=None)

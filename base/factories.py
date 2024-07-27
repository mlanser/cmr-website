from factory import Faker
from factory.django import DjangoModelFactory

from locations.models import Location


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    name = Faker('name')
    street = Faker('street_address')
    city = Faker('city')
    state = Faker('state')
    zip = Faker('zipcode')
    virtual = Faker('boolean', chance_of_getting_true=50)
    url = Faker('url')
    map = Faker('url')
    description = Faker('text', max_nb_chars=40, ext_word_list=None)
    # image = Faker('image_url', width=None, height=None, category=None, randomize=None)

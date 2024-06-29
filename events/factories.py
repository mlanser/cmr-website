from factory import Faker
from factory.django import DjangoModelFactory

from events.models import Event


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    title = Faker('sentence', nb_words=4, variable_nb_words=True)
    description = Faker('text', max_nb_chars=40, ext_word_list=None)
    date = Faker('date_time_this_year', before_now=True, after_now=False)
    location = Faker('city')

from datetime import timedelta

from factory import Faker
from factory.django import DjangoModelFactory

from accounts.models import CustomUser


class MemberProfileFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = Faker('first_name')
    # middleName = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    birthDate = Faker('date_of_birth', minimum_age=18, maximum_age=100)
    memberDate = Faker('date_this_decade', before_today=True, after_today=False)
    renewalDate = memberDate + timedelta(days=365)
    expireDate = memberDate + timedelta(days=365)
    bio = Faker('text', max_nb_chars=40, ext_word_list=None)
    # photo = Faker('image_url', width=None, height=None, category=None, randomize=None)
    # active = Faker('boolean', chance_of_getting_true=50)

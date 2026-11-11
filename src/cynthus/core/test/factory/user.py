"""User factory for the Cynthus project"""

import factory

from ...user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = 'Ada'
    last_name = factory.Sequence(lambda n: f'Tester{n}')
    email = factory.LazyAttribute(lambda user: f'{user.first_name}.{user.last_name}@example.com'.lower())

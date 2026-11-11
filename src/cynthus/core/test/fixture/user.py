"""User fixtures for the Cynthus project"""

from pytest import fixture

from ...user import User
from ..factory import (
    UserFactory,
)


@fixture
def user() -> User:
    return UserFactory()

"""User model class for the Cynthus project"""

from sqlalchemy.orm import Mapped, mapped_column

from cynthus.core.model.base import ModelBase


class User(ModelBase):
    __table_name__ = 'users'

    email: Mapped[str] = mapped_column(unique=True)

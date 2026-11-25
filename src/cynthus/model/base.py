"""Base ORM model class for the Cynthus project"""

from __future__ import annotations

import uuid

from sqlalchemy import MetaData, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """the base ORM model class from which all other ORM model classes inherit"""

    metadata = MetaData()

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

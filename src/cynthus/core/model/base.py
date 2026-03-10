"""Database model base class for the Cynthus project"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from sqlalchemy import func, MetaData
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData()
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    created_on: Mapped[datetime] = mapped_column(nullable=False, default=func.now())

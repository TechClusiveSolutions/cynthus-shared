"""Soft deletable base class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SoftDeletable(BaseModel):
    """
        A model whose deletion keeps it (ADR-011)

        Every delete is a soft delete: ``deleted_at`` is set and the object stays. Only an explicit data-removal request
        removes it for real. A thing deleted with what it holds shares one timestamp, so one restore brings back the
        same objects and nothing else.
    """

    deleted_at: datetime | None = Field(default=None, description='When the object was deleted, if it was')

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self, at: datetime | None = None) -> datetime:
        """Marks the object deleted and returns the time, so what it holds can share it."""

        self.deleted_at = at or datetime.now(timezone.utc)

        return self.deleted_at

    def restore(self) -> None:
        self.deleted_at = None

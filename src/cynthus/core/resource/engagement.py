"""Engagement resource model class for the Cynthus project"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, model_validator

from ..user import User
from .attendee import Attendee
from .place import Place
from .workspace_resource import WorkspaceResource


class Engagement(WorkspaceResource):
    """
        Represents an engagement: a gathering planned in a workspace

        It has a time period, a place, attendees with their food preferences, the materials needed and logistical notes.
        When it names no place it uses the workspace's default place.
    """

    starts_at: datetime
    ends_at: datetime
    place: Place | None = Field(default=None, description="Empty means the workspace's default place")
    attendees: list[Attendee] = Field(default_factory=list)
    managers: list[User] = Field(default_factory=list, description='Users who may manage the engagement besides its creator')
    materials: list[str] = Field(default_factory=list, description='What is needed, for example chairs or a projector')
    notes: str | None = Field(default=None, description='Logistical considerations')

    @model_validator(mode='after')
    def _check_period(self) -> Engagement:
        if self.ends_at <= self.starts_at:
            raise ValueError('an engagement ends after it starts')

        if self.place is not None and self.place.workspace.id_ != self.workspace.id_:
            raise ValueError('an engagement uses a place of its own workspace')

        return self

    def place_or(self, default: Place | None) -> Place | None:
        """The place the engagement uses: its own, else the workspace's default."""

        return self.place if self.place is not None else default

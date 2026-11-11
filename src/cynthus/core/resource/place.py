"""Place resource model class for the Cynthus project"""

from __future__ import annotations

from pydantic import Field

from .workspace_resource import WorkspaceResource


class Place(WorkspaceResource):
    """
        Represents a place where an engagement can be held (a venue)

        A workspace has at most one default place: the one an engagement uses when it names none (ADR-011). The database
        that will hold places enforces that; this class carries the flag.
    """

    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country: str | None = None
    capacity: int | None = Field(default=None, ge=1, description='How many people the place holds')
    is_default: bool = Field(default=False, description="The workspace's default place (at most one is live)")

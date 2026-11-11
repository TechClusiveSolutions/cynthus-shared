"""Attendee resource model class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class Attendee(BaseModel):
    """
        Represents someone invited to an engagement, with the food they cannot or will not eat

        An attendee is a user (``user_id``) or a guest who has no account (``name`` only).
    """

    name: str
    user_id: UUID | None = None
    food_preferences: list[str] = Field(default_factory=list, description='Allergies, diets and dislikes to plan the menu around')

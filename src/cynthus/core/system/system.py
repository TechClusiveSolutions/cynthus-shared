"""System class for the Cynthus project"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

import cynthus

SYSTEM_ID = UUID('10000000-1000-1000-1000-100000000000')
SYSTEM_VERSION = cynthus.__VERSION__


class System(BaseModel):
    """Represents the system"""

    id_: UUID = Field(default=SYSTEM_ID, frozen=True)
    name: str = Field(default='Cynthus Life', frozen=True)
    version: str = Field(default=SYSTEM_VERSION, frozen=True)

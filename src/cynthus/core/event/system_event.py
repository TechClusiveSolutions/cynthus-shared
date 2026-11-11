"""System Event class for the Cynthus project"""

from __future__ import annotations

from pydantic import Field

from ..system import System
from .event import Event


class SystemEvent(Event):
    """Represents an action taken on a resource by the System"""

    system: System = Field(default_factory=System)

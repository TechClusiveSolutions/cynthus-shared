"""System Event class for the Cynthus project"""

from __future__ import annotations

from .event import Event

from ..system import System


class SystemEvent(Event):
    """Represents an action taken on a resource by the System"""

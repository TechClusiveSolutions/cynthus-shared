"""Service Domain core model class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class ServiceDomain(str, Enum):
    """Represents a service application domain"""

    COMMERCE: str = 'commerce'
    CORE: str = 'core'
    HEALTH: str = 'health'
    INTELLIGENCE: str = 'intelligence'
    TRUST: str = 'trust'

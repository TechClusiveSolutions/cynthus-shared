"""Tenant Type resource model class for the Cynthus project"""

from __future__ import annotations

from enum import Enum


class TenantType(str, Enum):
    """Represents a tenant type resource"""

    PERSONAL: str = 'personal'
    ORGANIZATIONAL: str = 'organizational'

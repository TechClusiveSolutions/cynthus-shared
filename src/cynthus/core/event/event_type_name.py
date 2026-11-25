"""Event type name helper for the Cynthus project"""

from __future__ import annotations

import re


def event_type_name(class_name: str) -> str:
    """The snake_case ``class_name`` without a trailing ``Event`` (``InventoryLocationCreatedEvent`` is
    ``inventory_location_created``; a class named exactly ``Event`` is ``event``)"""

    name = class_name.removesuffix('Event') or class_name
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)

    return name.lower()

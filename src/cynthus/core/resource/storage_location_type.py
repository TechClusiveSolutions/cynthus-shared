"""Storage Location Type resource model class for the Cynthus project"""

from enum import Enum


class StorageLocationType(str, Enum):
    """Represents a storage location type resource"""

    AMBIENT: str = 'ambient'
    HEATED: str = 'heated'
    FROZEN: str = 'frozen'
    REFRIDGERATED: str = 'refridgerated'

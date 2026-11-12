"""Signal Domain Type class for the Cynthus project"""

from enum import Enum


class SignalDomainType(str, Enum):
    """Standardized signal domain mutations"""

    ANALYSIS: str = 'analysis'
    AUTH: str = 'auth'
    IDENTITY: str = 'identity'
    INTELLIGENCE: str = 'intelligence'
    INVENTORY: str = 'inventory'
    MEAL: str = 'meal'
    PROFILE: str = 'profile'
    RECIPE: str = 'recipe'
    SHOPPING_LIST: str = 'shopping_list'

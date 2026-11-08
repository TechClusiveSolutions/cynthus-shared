"""Public Recipe Recipe Signal Base class for the Cynthus project"""

from .public_recipe_base import PublicRecipeSignalBase


class PublicRecipeRecipeSignalBase(PublicRecipeSignalBase, abstract=True):
    """Intermediate base for all public recipe recipe signals. Sets the aggregate component."""

    aggregate = 'recipe'

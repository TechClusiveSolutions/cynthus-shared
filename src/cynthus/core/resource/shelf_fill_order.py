"""Shelf Fill Order resource model class for the Cynthus project"""

from enum import Enum


class ShelfFillOrder(str, Enum):
    """
        The order in which a shelf's positions are filled

        Each value names the corner the filling starts at and whether a row (horizontal) or a column (vertical) is filled
        first.
    """

    BACK_LEFT_HORIZONTAL: str = 'back_left_horizontal'
    BACK_LEFT_VERTICAL: str = 'back_left_vertical'
    BACK_RIGHT_HORIZONTAL: str = 'back_right_horizontal'
    BACK_RIGHT_VERTICAL: str = 'back_right_vertical'
    FRONT_LEFT_HORIZONTAL: str = 'front_left_horizontal'
    FRONT_LEFT_VERTICAL: str = 'front_left_vertical'
    FRONT_RIGHT_HORIZONTAL: str = 'front_right_horizontal'
    FRONT_RIGHT_VERTICAL: str = 'front_right_vertical'

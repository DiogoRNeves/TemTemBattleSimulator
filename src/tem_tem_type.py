from __future__ import annotations

import json
import math
import random
from enum import Enum, auto
from typing import Iterable, Iterator



class TemTemType(Enum):
    """Enumeration of all possible Temtem types."""
    NO_TYPE = auto()
    NEUTRAL = auto()
    WIND = auto()
    EARTH = auto()
    WATER = auto()
    FIRE = auto()
    NATURE = auto()
    ELECTRIC = auto()
    MENTAL = auto()
    DIGITAL = auto()
    MELEE = auto()
    CRYSTAL = auto()
    TOXIC = auto()

    def get_multiplier(self, *defenders: TemTemType) -> float:
        """Calculate the total type multiplier of the attacker TemTemType
        against multiple defender TemTemTypes.

        Args:
        - *defenders: One or more defender TemTemTypes against which the
                      attacker TemTemType's multiplier is to be calculated.

        Returns:
        - float: The total type multiplier of the attacker TemTemType against
                 all the defender TemTemTypes.
        """
        return math.prod([self._get_multiplier(defender) for defender in defenders])

    def _get_multiplier(self, defender_tem: TemTemType) -> float:
        """Calculate the type multiplier of the attacker TemTemType against
        a single defender TemTemType.

        Args:
        - defender: The defender TemTemType against which the attacker
                    TemTemType's multiplier is to be calculated.

        Returns:
        - float: The type multiplier of the attacker TemTemType against the
                 defender TemTemType.
        """
        return _multipliers[self][defender_tem]

    @staticmethod
    def from_string(temtem_type: str) -> TemTemType:
        """Return the corresponding TemTemType enum value for the given
        type string.

        Args:
        - type: The string representation of the TemTemType.

        Returns:
        - TemTemType: The corresponding TemTemType enum value.
        """
        return TemTemType.NO_TYPE if len(temtem_type) == 0 \
            else TemTemType[temtem_type.upper()]

    @staticmethod
    def get_random_type(*exclude_type: TemTemType) -> TemTemType:
        """Return a random TemTemType that is not in the exclude_type list.

        Args:
        - *exclude_type: A list of TemTemTypes that the returned TemTemType
                         should not be.

        Returns:
        - TemTemType: A random TemTemType that is not in the exclude_type list.
        """
        return random.choice([t for t in TemTemType if not t in exclude_type])


# __multipliers[attacker][defender] returns the multiplier. defaults to 1 on initialization
_multipliers: dict[TemTemType, dict[TemTemType, float]] = {
    attacker: {defender: 1 for defender in TemTemType} for attacker in TemTemType
}

with open("./temtem_api/weaknesses.json", encoding="utf8") as file:
    # Load its content and make a new dictionary
    d: dict[str, dict[str, float]] = json.load(file)

for atk_str, data in d.items():
    attacker = TemTemType.from_string(atk_str)
    for defender_str, multiplier in data.items():
        defender = TemTemType.from_string(defender_str)
        _multipliers[attacker][defender] = multiplier


class TemType(Iterable):
    """Class representing the type of a TemTem monster."""
    def __init__(
        self, primary_type: TemTemType, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> None:
        """
        Initializes a TemType object.

        Args:
        - primary_type (TemTemType): The primary type of the TemType.
        - secondary_type (TemTemType, optional): The secondary type of the TemType.
            Defaults to TemTemType.NO_TYPE.

        Raises:
        - AssertionError: If the primary_type is TemTemType.NO_TYPE.

        Returns:
        - None: This method doesn't return anything.
        """
        assert (
            primary_type != TemTemType.NO_TYPE
        ), "Primary type has to be a proper type."
        if primary_type == secondary_type:
            secondary_type = TemTemType.NO_TYPE
        self.__original_types: list[TemTemType] = [primary_type, secondary_type]
        self.__current_types: list[TemTemType] = self.__original_types.copy()

    @property
    def primary_type(self) -> TemTemType:
        """
        Gets the primary type of the TemType.

        Returns:
        - TemTemType: The primary type of the TemType.
        """
        return self.__current_types[0]

    @property
    def secondary_type(self) -> TemTemType:
        """
        Gets the secondary type of the TemType.

        Returns:
        - TemTemType: The secondary type of the TemType.
        """
        return self.__current_types[1]

    def __iter__(self) -> Iterator[TemTemType]:
        """
        Returns an iterator over the current types of the TemType.

        Returns:
        - Iterator[TemTemType]: An iterator over the current types of the TemType.
        """
        return self.__current_types.__iter__()

    def __repr__(self) -> str:
        """
        Returns a string representation of the current types of the TemType.

        Returns:
        - str: A string representation of the current types of the TemType.
        """
        return self.__current_types.__repr__()

from __future__ import annotations

import random
from abc import ABC
from typing import Callable, Mapping

import TemTemConstants
from Stat import Stat


class StatsInitializer(ABC, Mapping):
    """Class representing a set of initial stat values for a Temtem."""
    def __init__(
        self,
        min: int,
        max: int,
        values: dict[Stat, int],
        default_value: int | Callable[[int, int], int],
    ) -> None:
        """
        Initializes a StatsInitializer instance.

        Args:
        - min (int): The minimum value allowed for the stats.
        - max (int): The maximum value allowed for the stats.
        - values (dict[Stat, int]): A dictionary containing the initial values of each stat.
        - default_value (int | Callable[[int, int], int]): The default value for any stat that is not defined in
            the 'values' parameter. If an integer is provided, the same value will be used for all undefined stats.
            If a callable is provided, it will be called with 'min' and 'max' as arguments to calculate the default
            value for each undefined stat.

        Raises:
        - AssertionError: If any of the initial values is not within the specified range.

        Returns:
        - None.
        """
        super().__init__()
        t = {
            stat: values.get(
                stat,
                default_value(min, max) if callable(default_value) else default_value,
            )
            for stat in Stat
        }
        for val in t.values():
            assert (
                val >= min and val <= max
            ), f"Stat of {val} not allowed. Must be between {min} and {max}."

        self._values = t

    def __getitem__(self, i):
        """
        Gets the value of the specified stat.

        Args:
        - i (Stat): The stat to get the value of.

        Returns:
        - int: The value of the specified stat.
        """
        return self._values[i]

    def __len__(self):
        """
        Returns the number of stats.

        Returns:
        - int: The number of stats.
        """
        return len(self._values)

    def __iter__(self):
        """
        Returns an iterator over the stats.

        Returns:
        - Iterator[Stat]: An iterator over the stats.
        """
        return self._values.__iter__()


class SvsInitializer(StatsInitializer):
    """A class representing the initial values for a Temtem's SVs (single values)."""
    def __init__(
        self,
        values: dict[Stat, int] = {},
        default_value: int | Callable[[int, int], int] = random.randint,
    ) -> None:
        """
        Initializes the stats of a Temtem's SVs (single values).

        Args:
        - values (dict[Stat, int]): A dictionary with the desired values for each Stat.
        - default_value (int | Callable[[int, int], int]): A default value to use for any missing Stat.
            It can be either a fixed value or a callable that takes the min and max possible values as arguments.
        """
        super().__init__(TemTemConstants.MIN_SV, TemTemConstants.MAX_SV, values, default_value)


class TvsInitializer(StatsInitializer):
    """A class representing the initial values for a Temtem's TVs (training values)."""
    def __init__(
        self,
        values: dict[Stat, int] = {},
        default_value: int = 0,
    ) -> None:
        """
        Initializes the stats of a Temtem's TVs (training values).

        Args:
        - values (dict[Stat, int]): A dictionary with the desired values for each Stat.
        - default_value (int): A default value to use for any missing Stat.

        Methods:
        - is_ok(max_total: int) -> bool:
            Checks if the total value of all stats is less than or equal to the given max_total.
            Returns True if it is, False otherwise.
        """
        super().__init__(TemTemConstants.MIN_TV, TemTemConstants.MAX_TV, values, default_value)

    def is_ok(self, max_total: int) -> bool:
        """
        Checks if the total value of all stats is less than or equal to the given max_total.

        Args:
        - max_total (int): The maximum total value allowed.

        Returns:
        - bool: True if the total value of all stats is less than or equal to max_total, False otherwise.
        """
        return sum((i for i in self._values.values())) <= max_total


class BaseValueInitializer(StatsInitializer):
    """A class representing the initial values for a Temtem's base values."""
    def __init__(self, values: dict[Stat, int]) -> None:
        """
        Initializes the stats of a Temtem's base values.

        Args:
        - values (dict[Stat, int]): A dictionary with the desired values for each Stat.

        Raises:
        - AssertionError: If values does not contain all the possible Stat values.

        """
        # values must have all stats
        for stat in Stat:
            assert (
                stat in values.keys()
            ), f"Can't initialize stat {stat}, it is not allowed."        
        super().__init__(TemTemConstants.MIN_BASE_VALUE, TemTemConstants.MAX_BASE_VALUE, values, 0)

    
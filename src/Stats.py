from __future__ import annotations

import random
from typing import TypeVar

from typing_extensions import NotRequired, TypedDict

from . import TemTemConstants
from .Stat import Stat, StatValueType, TemStat
from .StatsInitializer import BaseValueInitializer, SvsInitializer, TvsInitializer

T = TypeVar("T")
U = TypeVar("U")


def array_sum(n: int, s: int, m: int) -> list[int]:
    """
    Generate a list of n random integers between 1 and m that sum up to s or as close as possible.

    Args:
        n (int): Length of the list to be generated.
        s (int): Desired sum of the list to be generated.
        m (int): Maximum possible integer value for the elements of the list to be generated.

    Returns:
        list[int]: A list of n random integers between 1 and m that sum up to s or as close as possible.

    Raises:
        AssertionError: If the provided inputs violate the following condition:
            m * n >= s and n > 0 and s > 0 and m > 0.
    """

    assert (
        n > 0 and s > 0 and m > 0 and m * n >= s
    ), f"Cant provide an array with length {n} and sum {s} having max element  {m}."

    # Initialize a list of n elements with 0s
    result = [0] * n

    # Keep track of indices that have not reached the maximum value of m
    not_maxed = [i for i in range(n)]

    # Loop until the desired sum is reached
    while sum(result) < s:

        # Pick a random index from the not_maxed list
        i = random.randint(0, len(not_maxed) - 1)
        j = not_maxed[i]

        # Get the current value of the element at index j
        current = result[j]

        # Generate a random integer between 1 and the remaining amount needed to reach the desired sum or m, whichever is smaller
        v = random.randint(1, min(m, s - sum(result)))

        # Set the new value of the element at index j to be the minimum of the random value v + the current value and m
        result[j] = min(v + current, m)

        # Remove index j from the not_maxed list if the new value of the element is equal to m
        if result[j] == m:
            not_maxed.remove(j)

    return result


def rand_values_dict_max_sum(keys: list[U], sum: int, max_element: int) -> dict[U, int]:
    """
    Returns a dictionary with random values as the values and the given keys as the keys. The sum of the values in
    the dictionary is equal to the given sum, and each value is less than or equal to the given max element.

    Args:
        keys (list[U]) List of keys to use for the dictionary.
        sum (int) The sum of all the values in the dictionary.
        max_element (int) The maximum value for any element in the dictionary.

    Returns:
        dict[U, int]: A dictionary with the given keys and random values
    """

    # Generate a list of random values that add up to the desired sum
    vals = array_sum(len(keys), sum, max_element)

    # Create a dictionary with the given keys and the random values
    return {keys[i]: vals[i] for i in range(len(keys))}


class StatsArguments(TypedDict):
    """
    Typed dictionary containing the arguments for initializing a `Stats` object.

    Attributes:
        base (BaseValueInitializer): The initial values for the Temtem's base stats.
        svs (Optional[SvsInitializer]): The initial values for the Temtem's SVs (single values).
            Defaults to None.
        tvs (Optional[TvsInitializer]): The initial values for the Temtem's TVs (training values).
            Defaults to None.
    """

    base: BaseValueInitializer
    svs: NotRequired[SvsInitializer]
    tvs: NotRequired[TvsInitializer]


class Stats:
    """
    A class for managing Temtem stats, including base values, SVs, and TVs.
    """

    def __init__(
        self, base: BaseValueInitializer, svs: SvsInitializer, tvs: TvsInitializer
    ) -> None:
        """
        Initialize a new Stats object.

        Args:
            base: A BaseValueInitializer object representing the base stats.
            svs: An SvsInitializer object representing the SVs.
            tvs: A TvsInitializer object representing the TVs.

        Raises:
            AssertionError: If the total TV value exceeds the maximum allowed value.
        """
        super().__init__()
        assert tvs.is_ok(
            TemTemConstants.MAX_TV_TOTAL
        ), f"TV totals are not OK for f{tvs}"
        self.__stats = {
            stat: TemStat(base[stat], svs[stat], tvs[stat], stat) for stat in Stat
        }

    def get_stat(self, stat: Stat, vt: StatValueType) -> int:
        """
        Get the current value of a stat, given the specified value type.

        Args:
            stat: The stat to retrieve the value of.
            vt: The type of value to retrieve.

        Returns:
            The current value of the specified stat, given the specified value type.
        """
        return self.__stats[stat].get_value(vt)

    def is_tvs_ok(self, increment: int = 0) -> bool:
        """
        Determine whether the current total TV value, plus the specified increment,
        exceeds the maximum allowed TV value.

        Args:
            increment: The amount by which to increment the total TV value.

        Returns:
            True if the total TV value, plus the specified increment, does not exceed the
            maximum allowed TV value; False otherwise.
        """
        return self.total_tvs + increment <= TemTemConstants.MAX_TV_TOTAL

    def change_tv(self, stat: Stat, amount: int):
        """
        Adjust the TV value for a given stat by the specified amount.

        Args:
            stat: The stat to adjust the TV value for.
            amount: The amount to adjust the TV value by.
        """
        amt = min(amount, self.available_tvs(stat))
        self.__stats[stat].change_tv(amt)

    def available_tvs(self, stat: Stat) -> int:
        """
        Determine the maximum number of TV points that can be assigned to a given stat.

        Args:
            stat: The stat to retrieve the maximum number of TV points for.

        Returns:
            The maximum number of TV points that can be assigned to the specified stat.
        """
        return max(
            TemTemConstants.MAX_TV_TOTAL - self.total_tvs,
            self.__stats[stat].available_tvs,
            0,
        )

    def __get_value_type_dict(self, vt: StatValueType) -> dict[Stat, int]:
        """
        Get a dictionary of all stat values, given the specified value type.

        Args:
            vt: The type of value to retrieve.

        Returns:
            A dictionary mapping each stat to its current value, given the specified value type.
        """
        return {stat: self.get_stat(stat, vt) for stat in Stat}

    @property
    def svs(self) -> dict[Stat, int]:
        """
        Get a dictionary of all stat values, given the SV value type.

        Returns:
            A dictionary mapping each stat to its current SV value.
        """
        return self.__get_value_type_dict(StatValueType.SV)

    @property
    def tvs(self) -> dict[Stat, int]:
        """
        Returns a dictionary with the current TV values for each Stat.
        """
        return self.__get_value_type_dict(StatValueType.TV)

    @property
    def total_tvs(self) -> int:
        """
        Returns the total number of TV points invested across all Stats.
        """
        return sum([self.get_stat(stat, StatValueType.TV) for stat in Stat])

    def __call__(self, level) -> dict[Stat, int]:
        """
        Returns a dictionary with the TemTem's stats at a given level.

        Args:
            level (int): The TemTem's level.

        Returns:
            A dictionary with the TemTem's stats at the given level.
        """
        return {stat: temstat(level) for stat, temstat in self.__stats.items()}

    def __repr__(self) -> str:
        """
        Returns a string representation of the Stats object.
        """
        return self.__stats.__repr__()


class CompetitiveStats(Stats):
    """
    A class representing the stats of a Temtem with competitive values.
    """

    def __init__(self, base: BaseValueInitializer, tvs: TvsInitializer) -> None:
        """
        Initializes Svs to the maximum allowed value and sets Tvs to a provided dictionary
        that has the sum of its values bounded by the maximum allowed TV value.

        Args:
            base (BaseValueInitializer): A dictionary that contains the initial values of the TemTem's base stats.
            tvs (TvsInitializer): A dictionary that contains the initial values of the TemTem's Tvs.

        Raises:
            AssertionError: If the total number of Tvs is not the maximum allowed TV value.

        """
        super().__init__(
            base, SvsInitializer(default_value=TemTemConstants.MAX_SV), tvs
        )
        assert (
            self.total_tvs == TemTemConstants.MAX_TV_TOTAL
        ), f"In competitive play we expect max TVs. You've passed in {self.total_tvs}."


class RandomStats(Stats):
    """
    A class representing the stats of a Temtem with random values.

    """

    def __init__(
        self,
        base: BaseValueInitializer,
        tvs: TvsInitializer = TvsInitializer(
            values=rand_values_dict_max_sum(
                Stat.to_list(), TemTemConstants.MAX_TV_TOTAL, TemTemConstants.MAX_TV
            )
        ),
    ) -> None:
        """
        Inherits from Stats and initializes SvsInitializer with default value of 0 and TvsInitializer with random values.

        Args:
            base (BaseValueInitializer): BaseValueInitializer object representing the Temtem's base values.
            tvs (TvsInitializer, optional): TvsInitializer object representing the Temtem's trained values. Defaults to TvsInitializer(values=rand_values_dict_max_sum(Stat.to_list(), TemTemConstants.MAX_TV_TOTAL, TemTemConstants.MAX_TV)).


        """
        super().__init__(base, SvsInitializer(), tvs)


class RandomEncounterStats(RandomStats):
    """
    A class representing the stats of a Temtem with random values obtained in a random encounter.

    """

    def __init__(self, base: BaseValueInitializer) -> None:
        """
        Inherits from RandomStats and initializes TvsInitializer with default value of 0.

        Args:
            base (BaseValueInitializer): BaseValueInitializer object representing the Temtem's base values.

        """
        super().__init__(base, tvs=TvsInitializer())

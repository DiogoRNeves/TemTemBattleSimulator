from __future__ import annotations

from enum import Enum, auto
from math import floor

from src.tem_tem_constants import MAX_TV, MAX_TV_TOTAL, MIN_TV
from src.json_typed_dict import TemTemStatsJson


class StatValueType(Enum):
    """
    An enumeration representing the different types of Stat values.

    Attributes:
        BS: Base stat value.
        TV: Training value.
        SV: Single value.
    """

    BS = auto()
    TV = auto()
    SV = auto()


class Stat(Enum):
    """
    An enumeration representing the different Stats in Temtem.

    Attributes:
        HP: Hit Points.
        STA: Stamina.
        SPD: Speed.
        ATK: Attack.
        DEF: Defense.
        SPATK: Special Attack.
        SPDEF: Special Defense.
    """

    HP = 0
    STA = 1
    SPD = 2
    ATK = 3
    DEF = 4
    SPATK = 5
    SPDEF = 6

    @classmethod
    def to_list(cls) -> list[Stat]:
        """
        Returns a list of all the Stat values.
        """
        return [i for i in cls]

    @classmethod
    def initializer_dict(cls, temtem: TemTemStatsJson) -> dict[Stat, int]:
        """
        Returns a dictionary of Stat values and their initial values from the given `temtem`.

        Args:
            temtem: A dictionary containing the initial stats of a Temtem.

        Returns:
            A dictionary of Stat values and their initial values.
        """
        return {i: temtem[str(i.name.lower())] for i in cls}

    @classmethod
    def initializer_dict_from_list(cls, values: list[int]) -> dict[Stat, int]:
        return {s: values[s.value] for s in cls}


class TemStat:
    """
    A class to represent a single stat of a Temtem.
    """

    def __init__(self, base: int, sv: int, tv: int, stat: Stat) -> None:
        """
        Initializes a new instance of the TemStat class.

        Args:
        - base (int): The base value of the stat.
        - sv (int): The single value of the stat.
        - tv (int): The total value of the stat.
        - stat (Stat): The type of the stat.

        Returns:
        - None.
        """
        self.__values = {
            StatValueType.BS: base,
            StatValueType.SV: sv,
            StatValueType.TV: tv,
        }
        self.__original_values = self.__values.copy()
        self.__stat = stat

    @property
    def available_tvs(self) -> int:
        """
        The amount of available TV points that can still be allocated to the stat.

        Returns:
        - int: The number of available TV points.
        """
        return MAX_TV - self.get_value(StatValueType.TV)

    @property
    def base(self) -> int:
        """
        The base value of the stat.

        Returns:
        - int: The base value of the stat.
        """
        return self.get_value(StatValueType.BS)

    @property
    def tv(self) -> int:
        """
        The TVs of the stat.

        Returns:
        - int: The TVs of the stat.
        """
        return self.get_value(StatValueType.TV)

    @property
    def sv(self) -> int:
        """
        The SVs of the stat.

        Returns:
        - int: The SVs of the stat.
        """
        return self.get_value(StatValueType.SV)

    def get_value(self, vt: StatValueType, original: bool = False) -> int:
        """
        Gets the value of the stat.

        Args:
        - vt (StatValueType): The type of the stat to retrieve the value from.
        - original (bool): Whether to retrieve the original value or not. Default is False.

        Returns:
        - int: The value of the stat.
        """
        src = self.__original_values if original else self.__values
        return src[vt]

    def change_tv(self, amount: int):
        """
        Changes the training value of the stat by adding or removing a certain amount.

        Args:
        - amount (int): The amount to add or remove from the training value.
        """
        self.__values[StatValueType.TV] = max(
            min(
                self.__values[StatValueType.TV] + min(amount, self.available_tvs),
                MAX_TV_TOTAL,
            ),
            MIN_TV,
        )

    def __calc_hp(self, level: int) -> int:
        """
        Calculates the HP stat.

        Args:
        - level (int): The level of the Temtem.

        Returns:
        - int: The total value of the HP stat.
        """
        a = ((1.5 * self.base) + self.sv + (self.tv / 5)) * level
        b = self.sv * self.base * level
        return floor((a / 80) + (b / 20000) + level + 15)

    def __calc_sta(self, level: int) -> int:
        """
        Calculates the STA stat.

        Args:
        - level (int): The level of the Temtem.

        Returns:
        - int: The total value of the STA stat.
        """
        a = self.sv * self.base * level
        b = self.tv * self.base * level
        return floor(
            (self.base / 4) + ((level**0.35) * 6) + (a / 20000) + (b / 30000)
        )

    def __calc_others(self, level: int) -> int:
        """
        Calculates the total value of the stat for all stats except for HP and STA.

        Args:
        - level (int): The level of the Temtem.

        Returns:
        - int: The total value of the stat.
        """
        a = ((1.5 * self.base) + self.sv + (self.tv / 5)) * level
        b = self.sv * self.base * level
        return floor((a / 100) + (b / 25000) + 10)

    def __call__(self, level: int) -> int:
        """
        Calculates the total value of the stat based on the given level.

        Args:
        - level (int): The level of the Temtem.

        Returns:
        - int: The total value of the stat.
        """
        match self.__stat:
            case Stat.HP:
                st = self.__calc_hp(level)
            case Stat.STA:
                st = self.__calc_sta(level)
            case _:
                st = self.__calc_others(level)

        return st  # TODO implement stages. status condition modifiers are applied later

    def __repr__(self):
        """
        Returns a string representation of the TemStat instance.

        Returns:
        - str: A string representation of the TemStat instance.
        """
        return self.__values.__repr__()

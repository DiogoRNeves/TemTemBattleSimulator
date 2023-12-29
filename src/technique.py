from __future__ import annotations

import json
import math
import random
from enum import Enum, auto
from typing import Iterable

from src.json_typed_dict import TechniqueJson
from src.tem_stat import Stat
from src.tem_tem_type import TemTemType, TemType

with open("./temtem_api/techniques.json", encoding="utf8") as file:
    # Load its content and make a new dictionary
    d: list[TechniqueJson] = json.load(file)

_techniques: dict[str, TechniqueJson] = {}
for t in d:
    _techniques[t["name"].lower()] = t

# ic| k: 'class'
#     set([t[k] for t in _techniques.values()]): {'Special', 'Status', 'Physical'}


class TechniqueClass(Enum):
    """
    An enumeration representing the class of a technique.

    The class of a technique determines which attack stat and defense stat are used
    when calculating damage.

    Attributes:
        SPECIAL (TechniqueClass): A technique that uses the special attack stat.
        STATUS (TechniqueClass): A technique that does not inflict damage.
        PHYSICAL (TechniqueClass): A technique that uses the physical attack stat.
    """
    SPECIAL = auto()
    STATUS = auto()
    PHYSICAL = auto()

    @staticmethod
    def from_string(cla: str) -> TechniqueClass:
        """Return the TechniqueClass instance that matches the given string.

        Args:
        - cla (str): A string that represents a TechniqueClass.

        Returns:
        - TechniqueClass: The TechniqueClass instance that matches the given string.

        Raises:
        - KeyError: If there is no TechniqueClass instance that matches the given string.
        """
        return TechniqueClass[cla.upper()]

    @property
    def atk_stat(self) -> Stat:
        """Return the Stat that corresponds to the attack attribute of this TechniqueClass.

        Returns:
        - Stat: The Stat that corresponds to the attack attribute of this TechniqueClass.

        Raises:
        - AssertionError: If this TechniqueClass is 'STATUS'.
        """
        assert (
            self != TechniqueClass.STATUS
        ), "A 'Status' technique does not inflict any damage."
        match self:
            case TechniqueClass.SPECIAL:
                return Stat.SPATK
            case TechniqueClass.PHYSICAL:
                return Stat.ATK

    @property
    def def_stat(self) -> Stat:
        """Return the Stat that corresponds to the defense attribute of this TechniqueClass.

        Returns:
        - Stat: The Stat that corresponds to the defense attribute of this TechniqueClass.

        Raises:
        - AssertionError: If this TechniqueClass is 'STATUS'.
        """
        assert (
            self != TechniqueClass.STATUS
        ), "A 'Status' technique does not inflict any damage."
        match self:
            case TechniqueClass.SPECIAL:
                return Stat.SPDEF
            case TechniqueClass.PHYSICAL:
                return Stat.DEF


# ic| k: 'targets'
#     set([t[k] for t in _techniques.values()]): {'All',
#                                                 'All Other Temtem',
#                                                 'Other Team or Ally',
#                                                 'Self',
#                                                 'Single Other Target',
#                                                 'Single Target',
#                                                 'Single Team'}


class TechniqueTargets(Enum):
    """
    An enumeration representing the possible targets of a technique.

    Attributes:
        ALL (TechniqueTargets): All temtem, including allies and foes.
        ALL_OTHER_TEMTEM (TechniqueTargets): All temtem other than the user.
        OTHER_TEAM_OR_ALLY (TechniqueTargets): An ally or a foe.
        SELF (TechniqueTargets): The user of the technique.
        SINGLE_OTHER_TARGET (TechniqueTargets): A single temtem other than the user.
        SINGLE_TARGET (TechniqueTargets): A single temtem, including allies and foes.
        SINGLE_TEAM (TechniqueTargets): All temtem on the user's team.
    """
    ALL = auto()
    ALL_OTHER_TEMTEM = auto()
    OTHER_TEAM_OR_ALLY = auto()
    SELF = auto()
    SINGLE_OTHER_TARGET = auto()
    SINGLE_TARGET = auto()
    SINGLE_TEAM = auto()

    @staticmethod
    def from_string(targets: str) -> TechniqueTargets:
        """Returns a TechniqueTargets instance based on the given string.

        Args:
        - targets (str): The string to match to a TechniqueTargets instance.

        Returns:
        - TechniqueTargets: The corresponding TechniqueTargets instance.

        """
        return TechniqueTargets[targets.replace(" ", "_").upper()]


# ic| k: 'priority'
# set([t[k] for t in _techniques.values()]):
#   {'low', 'veryhigh', 'high', 'normal', 'verylow', 'ultra'}


class TechniquePriority(Enum):
    """
    An enumeration representing the priority of a technique.

    The priority of a technique determines its turn order in battle.

    Attributes:
        LOW (TechniquePriority): A technique with low priority.
        VERYHIGH (TechniquePriority): A technique with very high priority.
        HIGH (TechniquePriority): A technique with high priority.
        NORMAL (TechniquePriority): A technique with normal priority.
        VERYLOW (TechniquePriority): A technique with very low priority.
        ULTRA (TechniquePriority): A technique with ultra high priority.
    """
    LOW = 0.5
    VERYHIGH = 1.75
    HIGH = 1.5
    NORMAL = 1
    # very low goes after everything
    VERYLOW = 0.00000001
    # ultra goes before everything, including switching
    ULTRA = 10000000

    @staticmethod
    def from_string(priority: str) -> TechniquePriority:
        """Returns a TechniquePriority instance based on the given string.

        Args:
        - priority (str): The string to match to a TechniquePriority instance.

        Returns:
        - TechniquePriority: The corresponding TechniquePriority instance.

        """
        return TechniquePriority[priority.upper()]


class Technique:
    """
    A class representing a technique used by a Temtem.
    """
    def __init__(self, name: str) -> None:
        """
        Initializes a Technique instance.

        Args:
        - name (str): The name of the technique.

        Raises:
        - AssertionError: If the specified technique name is not found in the list of techniques.
        """
        lookup_name: str = name.lower()
        assert lookup_name in _techniques, f"Technique not found: {name}"

        self.__technique_data = _techniques[lookup_name]
        self.__type: TemTemType = TemTemType.from_string(self.__technique_data["type"])
        self.__held: int = 0
        self.__priority: TechniquePriority = TechniquePriority.from_string(
            self.__technique_data["priority"]
        )
        self.__targets: TechniqueTargets = TechniqueTargets.from_string(
            self.__technique_data["targets"]
        )
        self.__class = TechniqueClass.from_string(
            self.__technique_data["class"]
        )

    @property
    def __name(self) -> str:
        return self.__technique_data["name"]

    @property
    def __hold(self) -> str:
        return self.__technique_data["hold"]

    @property
    def __stamina_cost(self) -> str:
        return self.__technique_data["staminaCost"]

    @property
    def __damage(self) -> str:
        return self.__technique_data["damage"]

    @staticmethod
    def get_random_technique(
        *temtem_type: TemTemType, classes: Iterable[TechniqueClass] = TechniqueClass
    ) -> Technique:
        """
        Returns a randomly chosen technique that matches the specified classes and types.

        Args:
        - classes (Iterable[TechniqueClass]): The list of technique classes to choose from.
        - *type (TemTemType): The list of Temtem types to choose from.

        Returns:
        - Technique: A randomly chosen technique.

        """
        names = [
            tech_name
            for tech_name, tech in _techniques.items()
            if (
                len(temtem_type) == 0 or TemTemType.from_string(tech["type"]) in temtem_type
            )
            and TechniqueClass.from_string(tech["class"]) in classes
        ]
        rand_name = random.choice(names)
        return Technique(rand_name)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def inflicts_damage(self) -> bool:
        return self.__class != TechniqueClass.STATUS

    @property
    def is_ready(self) -> bool:
        """
        Whether the technique is ready to be used.

        Returns:
        - bool: Whether the technique is ready to be used.
        """
        return self.__held >= self.__hold

    @property
    def atk_stat(self) -> Stat:
        """
        The attacking stat used by the technique.

        Returns:
        - Stat: The attacking stat used by the technique.
        """
        return self.__class.atk_stat

    @property
    def def_stat(self) -> Stat:
        """
        The defending stat used by the technique.

        Returns:
        - Stat: The defending stat used by the technique.
        """
        return self.__class.def_stat

    @property
    def type(self) -> TemTemType:
        """
        The type of the technique.

        Returns:
        - TemTemType: The type of the technique.
        """
        return self.__type

    def calculate_damage(
        self, atkr_lvl: int, atk: int, df: int, types: TemType, *extra_modifiers
    ) -> int:
        """
        Calculates the damage that the technique will inflict.

        Args:
        - atkr_lvl (int): The level of the attacking Temtem.
        - atk (int): The attacking stat of the attacking Temtem.
        - df (int): The defending stat of the defending Temtem.
        - types (TemType): The types of the attacking and defending Temtems.
        - *extra_modifiers: Any additional damage modifiers to be applied.

        Returns:
        - int: The amount of damage that the technique will inflict.
        """
        modifier = (
            math.prod(extra_modifiers) if len(extra_modifiers) > 0 else 1
        ) * self.type.get_multiplier(*types)
        return math.floor(
            (7 + (atkr_lvl / 200) * self.__damage * (atk / df)) * modifier
        )

    def increment_held(self, amount: int = 1):
        """
        Increases the held count of the technique by the given amount.

        Args:
        - amount (int, optional): The amount to increase the held count by. Defaults to 1.
        """
        self.__held += amount

    def reset_held(self):
        """
        Resets the held count of the technique to 0.
        """
        self.__held = 0

    def __str__(self) -> str:
        return f"{self.name}, {self.__hold} hold, {self.__targets.name}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the `Technique` object.

        Returns:
        - str: A string representation of the `Technique` object.
        """
        return {"name": self.__name, "type": self.type}.__repr__()

    def __eq__(self, __o: Technique) -> bool:
        return self.name == __o.name


if __name__ == "__main__":
    from icecream import ic

    ic(len(_techniques))
    for i in range(10):
        tp = TemTemType.get_random_type(TemTemType.NO_TYPE)
        t = Technique.get_random_technique(TechniqueClass, tp)
        ic(tp, t)

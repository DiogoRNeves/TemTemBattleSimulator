from __future__ import annotations

import random
from abc import ABC
from typing import Callable, Type, final

from typing_extensions import NotRequired, TypedDict
from .TechniqueSet import BattleTechniques, LearnableTechniques

from . import TemTemConstants
from .Stats import (
    CompetitiveStats,
    RandomEncounterStats,
    RandomStats,
    Stat,
    Stats,
    StatsArguments,
    SvsInitializer,
    TvsInitializer,
)
from .Technique import Technique, TechniqueClass
from .Tempedia import Tempedia
from .TemTemType import TemTemType, TemType


class TemSpeciesArg(TypedDict):
    id: int
    secondary_type: NotRequired[TemTemType]


class TemSpecies(ABC):
    """Abstract base class for all TemTem species."""

    def __init__(
        self, id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> None:
        """Create a new TemTem species.

        Args:
        - id (int): The species ID.
        - secondary_type (str or TemTemType, optional): The species' secondary type. Defaults to TemTemType.NO_TYPE.

        Raises:
        - AssertionError: If the species has a variable secondary type that is not specified, or if the species does not have a variable secondary type and one is specified.
        - AssertionError: If the specified secondary type conflicts with the species' original secondary type.
        """
        super().__init__()
        self._id = id
        self._base = Tempedia.get_base_value_initializer(id)
        self.__species_name = Tempedia.get_name(id)

        if self.__species_name.lower() in TemTemConstants.MULTIPLE_SECONDARY_TYPE:
            assert (
                secondary_type != TemTemType.NO_TYPE
            ), f"{self.__species_name} has a variable secondary type that must be specified."
        else:
            assert (
                secondary_type == TemTemType.NO_TYPE
            ), f"{self.__species_name} does not have a variable secondary type."

        t = Tempedia.get_types(id)
        if secondary_type != TemTemType.NO_TYPE:
            assert (
                t[1] == TemTemType.NO_TYPE
            ), f"{self.__species_name} has second type {t[1]} and it cannot be changed"
            t[1] = secondary_type
        self.__type = TemType(*t)

    @property
    def species_name(self) -> str:
        """Get the name of the species.

        Returns:
        - str: The name of the species.
        """
        return self.__species_name

    @property
    def primary_type(self) -> TemTemType:
        """Get the species' primary type.

        Returns:
        - TemTemType: The species' primary type.
        """
        return self.__type.primary_type

    @property
    def secondary_type(self) -> TemTemType:
        """Get the species' secondary type.

        Returns:
        - TemTemType: The species' secondary type.
        """
        return self.__type.secondary_type

    @property
    def types(self) -> TemType:
        """Get the species' types.

        Returns:
        - TemType: The species' types.
        """
        return self.__type

    @final
    def _get_latest_learnable_techniques(
        self,
        level: int,
        max_number_of_techniques: int = TemTemConstants.NUMBER_OF_BATTLE_TECHNIQUES,
    ) -> LearnableTechniques:
        return LearnableTechniques(
            Tempedia.get_latest_learnable_technique_names(
                self._id, level, max_number_of_techniques
            )
        )


class Tem(TemSpecies):
    def __init__(
        self,
        id: int,
        stat_cls: Type[Stats],
        battle_technique_names: list[str] = [],
        tvs: TvsInitializer | None = None,
        svs: SvsInitializer | None = None,
        level: int | Callable[[int, int], int] = random.randint,
        secondary_type: TemTemType = TemTemType.NO_TYPE,
        nickname: str = "",
    ) -> None:
        """
        Initializes a new Tem.

        Args:
        - id (int): The ID of the Tem species.
        - stat_cls (Type[Stats]): The class used to calculate the Tem's stats.
        - battle_technique_names (list[str], optional): The technique names to consider as battle ready. If none is passed we'll give the last 4 moves it can learn,
        - tvs (TvsInitializer | None, optional): The Tem's TV stats. Defaults to None.
        - svs (SvsInitializer | None, optional): The Tem's SV stats. Defaults to None.
        - level (int | Callable[[int, int], int], optional): The Tem's level or a callable function to generate it. Defaults to random.randint.
        - secondary_type (TemTemType, optional): The Tem's secondary type. Defaults to TemTemType.NO_TYPE.
        - nickname (str, optional): The Tem's nickname. Defaults to "".

        Returns:
        - None
        """
        kwargs: TemSpeciesArg = {"id": id}

        if Tempedia.get_name(id).lower() in TemTemConstants.MULTIPLE_SECONDARY_TYPE:
            if secondary_type == TemTemType.NO_TYPE:
                secondary_type = TemTemType.get_random_type(secondary_type)
            kwargs["secondary_type"] = secondary_type

        super().__init__(**kwargs)
        kargs: StatsArguments = {"base": self._base}
        if tvs is not None:
            kargs["tvs"] = tvs
        if svs is not None:
            kargs["svs"] = svs
        self.__stats = stat_cls(**kargs)
        self.__level = (
            level(TemTemConstants.TEM_MIN_LEVEL, TemTemConstants.TEM_MAX_LEVEL)
            if callable(level)
            else level
        )
        self.__nickname = nickname

        if len(battle_technique_names) == 0:
            battle_technique_names = super()._get_latest_learnable_techniques(
                self.__level
            ).names
        self.__battle_techniques = BattleTechniques(battle_technique_names)

        assert (
            self.__level >= TemTemConstants.TEM_MIN_LEVEL
            and self.__level <= TemTemConstants.TEM_MAX_LEVEL
        ), f"Level {level} is not allowed."

    @classmethod
    def from_random_encounter(
        cls, id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> Tem:
        """
        Creates a new Tem with random encounter stats.

        Args:
        - id (int): The ID of the Tem species.
        - secondary_type (TemTemType, optional): The Tem's secondary type. Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(id, RandomEncounterStats, secondary_type=secondary_type)

    @classmethod
    def from_random_stats(
        cls, id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> Tem:
        """
        Creates a new Tem with random stats.

        Args:
        - id (int): The ID of the Tem species.
        - secondary_type (TemTemType, optional): The Tem's secondary type. Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(id, RandomStats, secondary_type=secondary_type)

    @classmethod
    def from_competitive(
        cls,
        id: int,
        tvs: TvsInitializer,
        level=100,
        secondary_type: TemTemType = TemTemType.NO_TYPE,
    ) -> Tem:
        """
        Creates a new Tem with competitive stats.

        Args:
        - id (int): The ID of the Tem species.
        - tvs (TvsInitializer): The Tem's TV stats.
        - level (int, optional): The Tem's level. Defaults to 100.
        - secondary_type (TemTemType, optional): The Tem's secondary type. Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(
            id, CompetitiveStats, tvs=tvs, level=level, secondary_type=secondary_type
        )

    @classmethod
    def from_custom(
        cls,
        id: int,
        tvs: TvsInitializer,
        svs: SvsInitializer,
        level: int,
        battle_techniques: list[str],
        secondary_type: TemTemType = TemTemType.NO_TYPE,
        nickname: str = "",
    ) -> Tem:
        """
        Create a custom TemTem instance with specific TV, SV, and level.

        Args:
        - id (int): The ID of the TemTem species.
        - tvs (TvsInitializer): The TV values for the TemTem.
        - svs (SvsInitializer): The SV values for the TemTem.
        - level (int): The level of the TemTem.
        - secondary_type (TemTemType, optional): The secondary type of the TemTem. Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The custom TemTem instance.
        """
        return cls(
            id,
            Stats,
            tvs=tvs,
            svs=svs,
            level=level,
            secondary_type=secondary_type,
            battle_technique_names=battle_techniques,
            nickname=nickname,
        )

    @classmethod
    def from_data(
        cls,
        name: str,
        battle_techniques: list[str],
        svs: list[int] = [],
        tvs: list[int] = [],
        level: int = random.randint(
            TemTemConstants.TEM_MIN_LEVEL, TemTemConstants.TEM_MAX_LEVEL
        ),
        secondary_type: TemTemType = TemTemType.NO_TYPE,
        nickname: str = "",
    ) -> Tem:
        """
        Create a custom TemTem instance from raw data.

        Args:
        - name (str): Species name.
        - svs (list[int], optional): The SV values for the TemTem. Defaults to [].
        - tvs (list[int], optional): The TV values for the TemTem. Defaults to [].
        - level (int, optional): The level of the TemTem. Defaults to random.
        - secondary_type (TemTemType, optional): The secondary type of the TemTem. Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The custom TemTem instance.
        """
        id = Tempedia.get_id_from_name(name)
        assert len(svs) in [
            0,
            len(Stat),
        ], f"SVs list does not have acceptable size: {len(svs)=} {len(Stat)=}"
        svs_init = SvsInitializer(
            {} if len(svs) == 0 else Stat.initializer_dict_from_list(svs)
        )
        assert len(tvs) in [
            0,
            len(Stat),
        ], f"TVs list does not have acceptable size: {len(svs)=} {len(Stat)=}"
        tvs_init = TvsInitializer(
            {} if len(tvs) == 0 else Stat.initializer_dict_from_list(tvs)
        )

        return cls.from_custom(
            id, tvs_init, svs_init, level, battle_techniques, secondary_type, nickname
        )

    @property
    def display_name(self) -> str:
        """
        Get the display name of the TemTem, including the nickname if it has one.

        Returns:
        - str: The display name of the TemTem.
        """
        r = self.species_name
        if self.has_nickname:
            r = f"{self.nickname} ({r})"
        return f"{r} {{lv. {self.level}}}"

    @property
    def display_stats(self) -> str:
        return ", ".join([f"{s.name}: {v}" for s, v in self.stats.items()])

    @property
    def has_nickname(self) -> bool:
        """
        Check if the TemTem has a nickname.

        Returns:
        - bool: True if the TemTem has a nickname, False otherwise.
        """
        return len(self.nickname) > 0

    @property
    def nickname(self) -> str:
        """
        Get the nickname of the TemTem.

        Returns:
        - str: The nickname of the TemTem.
        """
        return self.__nickname

    @nickname.setter
    def nickname(self, n: str):
        """
        Set the nickname of the TemTem.

        Args:
        - n (str): The new nickname for the TemTem.
        """
        self.__nickname = n

    @property
    def level(self) -> int:
        """
        Get the level of the TemTem.

        Returns:
        - int: The level of the TemTem.
        """
        return self.__level

    @property
    def stats(self) -> dict[Stat, int]:
        """
        Get the stats of the TemTem at its current level.

        Returns:
        - dict[Stat, int]: A dictionary containing the stat values for the TemTem.
        """
        return self.__stats(self.level)

    @property
    def svs(self) -> dict[Stat, int]:
        """
        Get the SVs (single values) of the TemTem.

        Returns:
        - dict[Stat, int]: A dictionary containing the SV values for the TemTem.
        """
        return self.__stats.svs

    @property
    def battle_techniques(self) -> BattleTechniques:
        return self.__battle_techniques

    @property
    def tvs(self) -> dict[Stat, int]:
        """
        Get the TVs (training values) of the TemTem.

        Returns:
        - dict[Stat, int]: A dictionary containing the TV values for the TemTem.
        """
        return self.__stats.tvs

    def _get_type_multiplier(self, attaking_type: TemTemType) -> float:
        """
        Get the type multiplier for the TemTem based on the attacking type.

        Args:
        - attaking_type (TemTemType): The attacking type of the technique.

        Returns:
        - float: The type multiplier for the TemTem.
        """
        return attaking_type.get_multiplier(*self.types)

    def level_up(self, levels: int = 1):
        """
        Increases the Tem's level by the specified amount, up to the maximum level.

        Args:
        - levels (int): The number of levels to increase the Tem's level by. Defaults to 1.

        Returns:
        - None
        """
        self.__level = min(self.__level + levels, TemTemConstants.TEM_MAX_LEVEL)

    def calculate_atacking_damage(
        self, technique: Technique, def_tem: Tem, *extra_modifiers: float
    ) -> int:
        """
        Calculates the amount of damage a technique will deal to a defending Tem.

        Args:
        - technique (Technique): The technique being used to attack.
        - def_tem (Tem): The defending Tem that the technique is being used on.
        - *extra_modifiers (float): Any extra modifiers to apply to the damage calculation.

        Returns:
        - int: The amount of damage the technique will deal.
        """
        if not technique.inflicts_damage:
            return 0

        atk = self.stats[technique.atk_stat]
        df = def_tem.stats[technique.def_stat]

        if technique.type in self.types:
            extra_modifiers = extra_modifiers + (TemTemConstants.STAB_MODIFIER,)

        return technique.calculate_damage(
            self.level, atk, df, def_tem.types, *extra_modifiers
        )

    def calculate_defensive_damage(
        self, technique: Technique, atk_tem: Tem, *extra_modifiers: float
    ) -> int:
        """
        Calculates the amount of damage a technique will deal to a defending Tem.

        Args:
        - technique (Technique): The technique being used to attack.
        - atk_tem (Tem): The attacking Tem that is using the technique.
        - *extra_modifiers (float): Any extra modifiers to apply to the damage calculation.

        Returns:
        - int: The amount of damage the technique will deal.
        """
        return atk_tem.calculate_atacking_damage(technique, self, *extra_modifiers)

    def __str__(self) -> str:
        return f"{self.display_name} - {self.display_stats}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the Tem, including its name, types, level, stats, svs, and tvs.

        Returns:
        - str: A string representation of the Tem.
        """
        d = {
            "name": self.species_name,
            "types": self.types,
            "level": self.level,
            "stats": self.stats,
            "svs": self.svs,
            "tvs": self.tvs,
        }
        return d.__repr__()


if __name__ == "__main__":

    from icecream import ic

    n = Tempedia.size()
    t_enc = Tem.from_random_encounter(id=random.randint(1, n))
    t_rand = Tem.from_random_stats(id=random.randint(1, n))
    t_comp = Tem.from_competitive(
        id=Tempedia.get_id_from_name("hedgine"),
        tvs=TvsInitializer({Stat.SPD: 500, Stat.SPATK: 500}),
    )
    koish = Tem.from_random_encounter(id=143)
    chromeon = Tem.from_random_encounter(id=4, secondary_type=TemTemType.DIGITAL)

    ic(t_enc, t_rand, t_comp, koish, chromeon)

    effectiveness = {tp: t_rand._get_type_multiplier(tp) for tp in TemTemType}
    ic(t_rand.species_name, t_rand.types, effectiveness)

    tech = Technique.get_random_technique(
        [c for c in TechniqueClass if c != TechniqueClass.STATUS], *t_rand.types
    )
    damage = t_rand.calculate_atacking_damage(tech, t_enc)

    ic(tech, damage)

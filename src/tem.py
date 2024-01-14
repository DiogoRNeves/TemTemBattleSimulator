from __future__ import annotations
from dataclasses import dataclass, field

import random
from abc import ABC
from typing import Callable, Optional, Self, Type, final

from typing_extensions import NotRequired, TypedDict
from src.technique_set import BattleTechniques, LearnableTechniques

import src.tem_tem_constants as TemTemConstants
from src.stats import (
    CompetitiveStats,
    RandomEncounterStats,
    RandomStats,
    Stat,
    Stats,
    StatsArguments,
    SvsInitializer,
    TvsInitializer,
)
from src.technique import Technique, TechniqueClass
from src.tempedia import Tempedia
from src.tem_tem_type import TemTemType, TemType


class TemSpeciesArg(TypedDict):
    species_id: int
    secondary_type: NotRequired[TemTemType]


class TemSpecies(ABC):
    """Abstract base class for all TemTem species."""

    def __init__(
        self, species_id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> None:
        """Create a new TemTem species.

        Args:
        - id (int): The species ID.
        - secondary_type (str or TemTemType, optional): The species' secondary type.
            Defaults to TemTemType.NO_TYPE.

        Raises:
        - AssertionError: If the species has a variable secondary type that is not specified,
            or if the species does not have a variable secondary type and one is specified.
        - AssertionError: If the specified secondary type conflicts with the species'
            original secondary type.
        """
        super().__init__()
        self._id = species_id
        self._base = Tempedia.get_base_value_initializer(species_id)
        self.__species_name = Tempedia.get_name(species_id)

        if self.__species_name.lower() in TemTemConstants.MULTIPLE_SECONDARY_TYPE:
            assert (
                secondary_type != TemTemType.NO_TYPE
            ), f"{self.__species_name} has a variable secondary type that must be specified."
        else:
            assert (
                secondary_type == TemTemType.NO_TYPE
            ), f"{self.__species_name} does not have a variable secondary type."

        t = Tempedia.get_types(species_id)
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

@dataclass(frozen=True)
class SpeciesIdentifier():
    species_id: int

    @classmethod
    def from_species_name(cls, species_name: str) -> Self:
        return cls(Tempedia.get_id_from_name(species_name))


# TODO inject random
@dataclass(frozen=True)
class TemBattleConfig:
    stat_cls: Type[Stats] = Stats
    battle_technique_names: list[str] = field(default_factory=list)
    tvs: Optional[TvsInitializer] = None
    svs: Optional[SvsInitializer] = None
    level: int | Callable[[int, int], int] = random.randint

    @classmethod
    def from_data(
        cls,
        battle_techniques: list[str],
        tvs: Optional[list[int]] = None,
        svs: Optional[list[int]] = None,
        level: int = random.randint(
            TemTemConstants.TEM_MIN_LEVEL, TemTemConstants.TEM_MAX_LEVEL
        )
    ) -> Self:
        if svs is None:
            svs = []

        if tvs is None:
            tvs = []

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

        return cls(
            battle_technique_names=battle_techniques,
            level=level,
            tvs=tvs_init,
            svs=svs_init
        )


@dataclass(frozen=True)
class TemSpeciesConfig:
    # name and id will be muttually exclusiva. will populate id on passing the name
    species_identifier: SpeciesIdentifier
    secondary_type: TemTemType = TemTemType.NO_TYPE


    @classmethod
    def from_data(cls, species_name: str, secondary_type: Optional[TemTemType] = None) -> Self:

        species_identifier = SpeciesIdentifier.from_species_name(species_name)

        return cls(
                species_identifier=species_identifier
            ) if secondary_type is None \
              else cls(
                species_identifier=species_identifier,
                secondary_type=secondary_type
            )


class Tem(TemSpecies):
    def __init__(
            self,
            species_config: TemSpeciesConfig,
            battle_config: TemBattleConfig,
            nickname: str = ""
    ) -> None:
        """
        Initializes a new Tem.
        """

        kwargs: TemSpeciesArg = {"species_id":
                                 species_config.species_identifier.species_id}

        if Tempedia.get_name(
            species_config.species_identifier.species_id
        ).lower() in TemTemConstants.MULTIPLE_SECONDARY_TYPE:
            #if secondary_type == TemTemType.NO_TYPE:
            #    secondary_type = TemTemType.get_random_type(secondary_type)
            kwargs["secondary_type"] = TemTemType.get_random_type(species_config.secondary_type) \
                if species_config.secondary_type == TemTemType.NO_TYPE \
                    else species_config.secondary_type

        super().__init__(**kwargs)
        kargs: StatsArguments = {"base": self._base}
        if battle_config.tvs is not None:
            kargs["tvs"] = battle_config.tvs
        if battle_config.svs is not None:
            kargs["svs"] = battle_config.svs
        self.__stats = battle_config.stat_cls(**kargs)
        self.__level = (
            battle_config.level(
                TemTemConstants.TEM_MIN_LEVEL, TemTemConstants.TEM_MAX_LEVEL
            ) if callable(battle_config.level)
                else battle_config.level
        )
        self.__nickname = nickname

        battle_technique_names = battle_config.battle_technique_names \
            if any(battle_config.battle_technique_names) \
                else super()._get_latest_learnable_techniques(
                    self.__level
                ).names

        self.__battle_techniques = BattleTechniques(battle_technique_names)
        self.__hp = self.stats[Stat.HP]

        assert (
            TemTemConstants.TEM_MIN_LEVEL <= self.__level <= TemTemConstants.TEM_MAX_LEVEL
        ), f"Level {battle_config.level} is not allowed."

    @classmethod
    def from_random_encounter(
        cls, species_id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> Self:
        """
        Creates a new Tem with random encounter stats.

        Args:
        - id (int): The ID of the Tem species.
        - secondary_type (TemTemType, optional): The Tem's secondary type.
            Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(
            TemSpeciesConfig(
                SpeciesIdentifier(species_id),
                secondary_type=secondary_type
            ),
            TemBattleConfig(
                RandomEncounterStats
            )
        )

    @classmethod
    def from_random_stats(
        cls, species_id: int, secondary_type: TemTemType = TemTemType.NO_TYPE
    ) -> Self:
        """
        Creates a new Tem with random stats.

        Args:
        - id (int): The ID of the Tem species.
        - secondary_type (TemTemType, optional): The Tem's secondary type.
            Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(
            TemSpeciesConfig(
                SpeciesIdentifier(species_id),
                secondary_type=secondary_type
            ),
            TemBattleConfig(
                RandomStats
            )
        )

    @classmethod
    def from_competitive(
        cls,
        species_id: int,
        tvs: TvsInitializer,
        level=100,
        secondary_type: TemTemType = TemTemType.NO_TYPE,
    ) -> Self:
        """
        Creates a new Tem with competitive stats.

        Args:
        - id (int): The ID of the Tem species.
        - tvs (TvsInitializer): The Tem's TV stats.
        - level (int, optional): The Tem's level. Defaults to 100.
        - secondary_type (TemTemType, optional): The Tem's secondary type.
            Defaults to TemTemType.NO_TYPE.

        Returns:
        - Tem: The newly created Tem.
        """
        return cls(
            TemSpeciesConfig(
                SpeciesIdentifier(species_id),
                secondary_type=secondary_type
            ),
            TemBattleConfig(
                CompetitiveStats,
                tvs=tvs,
                level=level
            )
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
    def nickname(self, nckname: str):
        """
        Set the nickname of the TemTem.

        Args:
        - n (str): The new nickname for the TemTem.
        """
        self.__nickname = nckname

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

    @property
    def current_hp(self) -> int:
        return self.__hp

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    def _get_type_multiplier(self, attacking_type: TemTemType) -> float:
        """
        Get the type multiplier for the TemTem based on the attacking type.

        Args:
        - attaking_type (TemTemType): The attacking type of the technique.

        Returns:
        - float: The type multiplier for the TemTem.
        """
        return attacking_type.get_multiplier(*self.types)

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
        Returns a string representation of the Tem, including its name, types,
            level, stats, svs, and tvs.

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
    from typing import Final

    NUMBER_OF_TEMTEMS: Final[int] = Tempedia.size()
    t_enc = Tem.from_random_encounter(species_id=random.randint(1, NUMBER_OF_TEMTEMS))
    t_rand = Tem.from_random_stats(species_id=random.randint(1, NUMBER_OF_TEMTEMS))
    t_comp = Tem.from_competitive(
        species_id=Tempedia.get_id_from_name("hedgine"),
        tvs=TvsInitializer({Stat.SPD: 500, Stat.SPATK: 500}),
    )
    koish = Tem.from_random_encounter(species_id=143)
    chromeon = Tem.from_random_encounter(species_id=4, secondary_type=TemTemType.DIGITAL)

    ic(t_enc, t_rand, t_comp, koish, chromeon)

    effectiveness = {tp: tp.get_multiplier(*t_rand.types) for tp in TemTemType}
    ic(t_rand.species_name, t_rand.types, effectiveness)

    tech = Technique.get_random_technique(
        *t_rand.types,
        classes=[c for c in TechniqueClass if c != TechniqueClass.STATUS]
    )
    damage = t_rand.calculate_atacking_damage(tech, t_enc)

    ic(tech, damage)


import json
import random
import re
from typing import Callable, Tuple

from src.json_typed_dict import TemTemJson
from src.tem_stat import Stat
from src.stats_initializer import BaseValueInitializer
import src.tem_tem_constants as TemTemConstants
from src.tem_tem_type import TemTemType


with open("./temtem_api/temtems.json", encoding="utf8") as file:
    # Load its content and make a new dictionary
    d: list[TemTemJson] = json.load(file)

_tems: dict[int, TemTemJson] = {}

for r in d:
    # replace the (Water) and (Digital) on koish and chromeon
    r["name"] = re.sub(r"\s+\(\w+\)(\s+)?","", r["name"])
    i = r["number"]
    _tems[i] = r


class Tempedia():
    """
    A class that provides access to the temtem database.
    """
    @staticmethod
    def get_base_value_initializer(species_id: int) -> BaseValueInitializer:
        """
        Returns a new BaseValueInitializer object that initializes the base values
            of a temtem with the given id.

        Args:
        - id (int): The id of the temtem.

        Returns:
        - BaseValueInitializer: A new BaseValueInitializer object.
        """
        return BaseValueInitializer(Stat.initializer_dict(_tems[species_id]["stats"]))

    @staticmethod
    def _get_random_id_from_filter(
        fltr: Callable[[Tuple[int, TemTemJson]], bool]
    ) -> int:
        """
        Returns a random id of a temtem that satisfies the given filter.

        Args:
        - fltr (Callable[[Tuple[int, TemTemJson]], bool]): A function that
            returns True for temtems that should be considered.

        Returns:
        - int: A random id of a temtem that satisfies the given filter.

        Raises:
        - AssertionError: If there are no temtems that satisfy the given filter.
        """
        l = dict(filter(fltr, _tems.items()))
        assert len(l) > 0, "No results for given filter."
        return random.choice(list(l.keys()))

    @staticmethod
    def get_random_atk_id() -> int:
        """
        Returns the id of a temtem that has a higher atk stat than spatk stat.

        Returns:
        - int: The id of a temtem that has a higher atk stat than spatk stat.
        """
        fltr: Callable[[Tuple[int, TemTemJson]], bool] = (
            lambda a: a[1]["stats"]["atk"] > a[1]["stats"]["spatk"]
        )
        return Tempedia._get_random_id_from_filter(fltr)

    @staticmethod
    def get_random_spatk_id() -> int:
        """
        Returns the id of a temtem that has a higher spatk stat than atk stat.

        Returns:
        - int: The id of a temtem that has a higher spatk stat than atk stat.
        """
        fltr: Callable[[Tuple[int, TemTemJson]], bool] = (
            lambda a: a[1]["stats"]["spatk"] > a[1]["stats"]["atk"]
        )
        return Tempedia._get_random_id_from_filter(fltr)


    @staticmethod
    def get_random_id() -> int:
        """
        Returns the id of a random temtem.

        Returns:
        - int: The id of a random temtem.
        """
        fltr: Callable[[Tuple[int, TemTemJson]], bool] = (
            lambda a: True
        )
        return Tempedia._get_random_id_from_filter(fltr)

    @staticmethod
    def get_id_from_name(name: str) -> int:
        """
        Returns the id of a temtem with the given name.

        Args:
        - name (str): The name of the temtem.

        Returns:
        - int: The id of the temtem.

        Raises:
        - AssertionError: If there are no temtems with the given name.
        """
        fltr: Callable[[Tuple[int, TemTemJson]], bool] = (
            lambda a: a[1]["name"].lower() == name.lower()
        )
        try:
            species_id = Tempedia._get_random_id_from_filter(fltr)
        except AssertionError as e:
            raise AssertionError(f"No temtems named {name}.") from e
        return species_id

    @staticmethod
    def get_name(species_id: int) -> str:
        """
        Returns the name of a temtem with the given id.

        Args:
        - id (int): The id of the temtem.

        Returns:
        - str: The name of the temtem.
        """
        return _tems[species_id]["name"]

    @staticmethod
    def get_types(species_id: int) -> list[TemTemType]:
        """
        Returns the types of a temtem with the given id.

        Args:
        - id (int): The id of the temtem.

        Returns:
        - list[TemTemType]: A list containing the types of the temtem.
        """
        types = _tems[species_id]["types"]
        return [
            TemTemType.from_string(types[0]),
            TemTemType.from_string(types[1]) if len(types) > 1 else TemTemType.NO_TYPE,
        ]

    @staticmethod
    def get_latest_learnable_technique_names(
        tem_id: int,
        level: int,
        max_number_of_techniques: int
    ) -> list[str]:
        assert TemTemConstants.TEM_MIN_LEVEL <= level \
            <= TemTemConstants.TEM_MAX_LEVEL, f"Level not allowed: {level=}"

        # always return at least one technique name
        max_number_of_techniques = max(1, max_number_of_techniques)

        techs = list(
            filter(
                lambda t: t.get("levels", level + 1) <= level,
                _tems[tem_id]["techniques"]
            )
        )
        techs.sort(key=lambda t: t.get("levels", 0), reverse=True)

        return [t["name"] for t in techs[:max_number_of_techniques]]

    @staticmethod
    def get_names() -> list[str]:
        return [t["name"] for t in _tems.values()]

    @staticmethod
    def size() -> int:
        """
        Returns the number of temtems in the database.

        Returns:
        - int: The number of temtems in the database.
        """
        return len(_tems)

if __name__=='__main__':
    from icecream import ic

    ic([f"{t['name']}: {t['types']}" for t in _tems.values()])

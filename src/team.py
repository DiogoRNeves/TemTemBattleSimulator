from abc import ABC
from typing import Final, Iterable, TypeVar

from src.tem import Tem
import src.tem_tem_constants as TemTemConstants


class Team(ABC):
    def __init__(self, max_team_size: int, tems: Iterable[Tem]):
        """
        Initializes a new instance of the Team class.

        Args:
        - max_team_size (int): The maximum size of the team.
        - tems (Iterable[Tem]): An iterable of Tem objects to be included in the team.
        """
        tem_list = list(set(tems))  # no dupes.
        list_size = len(tem_list)
        assert (
            0 <list_size <= max_team_size
        ), f"Invalid team size: {list_size}"

        self.__max_team_size: Final[int] = max_team_size
        self.__tems = tem_list

    def add(self, tem: Tem):
        """
        Adds a Tem object to the team.

        Args:
        - tem (Tem): The Tem object to add to the team.

        Raises:
        - ValueError: If the team is already at its maximum size or if the Tem object
            is already in the team.
        """
        if len(self.__tems) == self.__max_team_size:
            raise ValueError(
                f"Cannot add Tem to team - team already has maximum size of {self.__max_team_size}."
            )

        if tem in self.__tems:
            raise ValueError(f"Cannot add Tem to team - Tem already in team: {tem.display_name=}")

        self.__tems.append(tem)

    def remove(self, tem: Tem):
        if tem not in self.__tems:
            raise ValueError(f"Cannot remove Tem from team - Tem not in team: {tem.display_name=}")

        self.__tems.remove(tem)

    def __call__(self, species_name_or_nickname: str) -> Tem:
        """
        Gets a Tem object from the team by its species name or nickname.

        Args:
        - species_name_or_nickname (str): The name to search for of the Tem to retrieve.

        Returns:
        - Tem: The Tem object with the specified species name or nickname.

        Raises:
        - KeyError: If there is no Tem object with the specified species
            name or nickname in the team.
        """

        for t in self.__tems:
            if species_name_or_nickname.lower() in (t.nickname.lower(), t.species_name.lower()):
                return t

        raise KeyError(f"No temtem found in team with {species_name_or_nickname=}")

    def __getitem__(self, index: int) -> Tem:
        """
        Gets a Tem object from the team by its index.

        Args:
        - index (int): The index of the Tem to retrieve.

        Returns:
        - Tem: The Tem object at the specified index.
        """
        return self.__tems[index]

    def __len__(self) -> int:
        """
        Gets the number of Tem objects in the team.

        Returns:
        - int: The number of Tem objects in the team.
        """
        return len(self.__tems)

    def __iter__(self):
        return self.__tems.__iter__()

    def __repr__(self):
        return [
            f"level {t.level} {t.display_name} with techs:" + \
                f"{t.battle_techniques.names}" for t in self
        ].__repr__()


TeamT = TypeVar('TeamT', bound=Team)

class CompetitiveTeam(Team):
    """A class representing a team used in a competitive battle"""

    def __init__(self, tems: Iterable[Tem]):
        """
        Initializes a new instance of the CompetitiveTeam class.

        Args:
        - tems (Iterable[Tem]): An iterable of Tem objects to be included in the team.
        """
        # TODO validate all species are different
        super().__init__(TemTemConstants.COMPETITIVE_TEAM_SIZE, tems)


class PlaythroughTeam(Team):
    """A class representing a team used in a playthrough"""

    def __init__(self, tems: Iterable[Tem]):
        """
        Initializes a new instance of the PlaythroughTeam class.

        Args:
        - tems (Iterable[Tem]): An iterable of Tem objects to be included in the team.
        """
        super().__init__(TemTemConstants.PLAYTHROUGH_TEAM_SIZE, tems)

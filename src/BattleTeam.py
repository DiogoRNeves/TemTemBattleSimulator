
from enum import auto
from .Tem import Tem
from .patterns.SequentialEnum import SequentialEnum


class TeamBattlePosition(SequentialEnum):
    RIGHT = auto()
    LEFT = auto()

class Teams(SequentialEnum):    
    ORANGE = auto()
    BLUE = auto()


class BattleTeam:
    def __init__(self, active: list[Tem], bench: list[Tem]):
        raise NotImplementedError

class BattleTeams:
    def __init__(self, teams: dict[Teams, BattleTeam]):
        raise NotImplementedError


from enum import auto
from typing import Self
from .BattleAction import TurnAction
from .BattleTeam import Teams
from .Team import Team
from .patterns.SequentialEnum import SequentialEnum


class BattlePhase(SequentialEnum):
    NOT_STARTED = auto()
    BEFORE_COMBAT = auto()
    BATTLE = auto()
    AFTER_COMBAT = auto()
    FINISHED = auto()

    def next(self) -> Self:
        return super().next(False)
    
    def prev(self) -> Self:
        return super().prev(False)

class BattleState():
    def __init__(self, team_orange: Team, team_blue: Team):
        self.__teams: dict[Teams, Team] = {
            Teams.ORANGE: team_orange,
            Teams.BLUE: team_blue,
        }
        self.__speed_arrow: Teams = Teams.BLUE
        self.__phase: BattlePhase = BattlePhase.NOT_STARTED
        self.__reset_phase_turn()
        self.__history: dict[BattlePhase, list[TurnAction]] = {} 
        
    @property
    def phase(self) -> tuple[BattlePhase, int]:
        return (self.__phase, self.__phase_turn)
    
    def __reset_phase_turn(self):
        self.__phase_turn: int = 0

    def speed_tie(self) -> Team:
        t = self.__teams[self.__speed_arrow]
        self.__speed_arrow = self.__speed_arrow.next()
        return t
    
    def next_phase(self) -> BattlePhase:
        self.__phase = self.__phase.next()
        self.__reset_phase_turn()
        return self.phase[0]





from __future__ import annotations
from enum import auto
from typing import Callable, Self
from .BattleAction import TeamAction, TurnAction
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


# TODO
class SidedBattleState():
    def __init__(self, side: Team):
        self.__side = side

    @property
    def side(self) -> Team:
        return self.__side

class BattleState():
    def __init__(self, team_orange: Team, team_blue: Team):
        self.__teams: dict[Teams, Team] = {
            Teams.ORANGE: team_orange,
            Teams.BLUE: team_blue,
        }
        self.__speed_arrow: Teams = Teams.BLUE
        self.__phase: BattlePhase = BattlePhase.NOT_STARTED
        self.__reset_phase_turn()
        self.__history: dict[BattlePhase, list[TurnAction]] = {} # proper class ?
        self.clear_action_selection()
    
    
    @property
    def selected_actions(self) -> TurnAction:
        raise NotImplementedError

    @property
    def phase(self) -> tuple[BattlePhase, int]:
        return (self.__phase, self.__phase_turn)
    
    @property
    def is_actions_selected(self) -> bool:
        return self.__turn_action.is_ready
    
    @property
    def is_actions_generated(self) -> bool:
        raise NotImplementedError
    
    def __reset_phase_turn(self):
        self.__phase_turn: int = 0                

    def clear_action_selection(self):
        self.__turn_action: TurnAction = TurnAction()

    def clear_generated_actions(self):
        raise NotImplementedError

    def speed_tie(self) -> Team:
        t = self.__teams[self.__speed_arrow]
        self.__speed_arrow = self.__speed_arrow.next()
        return t
    
    def next_phase(self) -> BattlePhase:
        self.__phase = self.__phase.next()
        self.__reset_phase_turn()
        return self.phase[0]
    
    def is_team_action_selected(self, team: Teams) -> bool:
        return self.__turn_action.has_team_action(team)
    
    def for_side(self, side: Teams) -> SidedBattleState:
        raise NotImplementedError
    
    def select_action(self, action: TeamAction, team: Teams):
        raise NotImplementedError
    

from __future__ import annotations
from enum import auto
from typing import Self
from src.battle_action import TeamAction, TurnAction
from src.battle_team import TeamBattlePosition, Teams
from src.team import Team
from src.patterns.sequential_enum import SequentialEnum


class BattlePhase(SequentialEnum):
    NOT_STARTED = auto()
    BEFORE_COMBAT = auto()
    BATTLE = auto()
    AFTER_COMBAT = auto()
    FINISHED = auto()

    def next(self, loop: bool = False) -> Self:
        return super().next(loop)

    def prev(self, loop: bool = False) -> Self:
        return super().prev(loop)

# TODO
class BattleResult():
    def __init__(self):
        raise NotImplementedError

# TODO
class SidedBattleState():
    def __init__(self, side: Teams, possible_actions: list[TeamAction]):
        self.__side = side
        self.__possible_actions = possible_actions

    @property
    def side(self) -> Teams:
        return self.__side

    @property
    def possible_actions(self) -> list[TeamAction]:
        return self.__possible_actions

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

    @property
    def is_over(self) -> bool:
        return self.__phase == BattlePhase.FINISHED

    @property
    def result(self) -> BattleResult:
        assert self.is_over, "Battle must be over to have a result"
        raise NotImplementedError

    def __reset_phase_turn(self):
        self.__phase_turn: int = 0

    def team_has_actions(self, team: Teams) -> bool:
        raise NotImplementedError

    def clear_action_selection(self):
        self.__turn_action: TurnAction = TurnAction()

    def speed_tie(self) -> Teams:
        self.__speed_arrow = self.__speed_arrow.next()
        return self.__speed_arrow

    def next_phase(self) -> BattlePhase:
        self.__phase = self.__phase.next()
        self.__reset_phase_turn()
        return self.phase[0]

    def is_team_action_selected(self, team: Teams) -> bool:
        return self.__turn_action.has_team_action(team)

    def team_has_temtem_in_position(self, team: Teams, position: TeamBattlePosition):
        # TODO implement a battlefield that takes care of the positions
        raise NotImplementedError

    def for_side(self, side: Teams) -> SidedBattleState:
        raise NotImplementedError

    def select_action(self, action: TeamAction, team: Teams):
        raise NotImplementedError

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import auto
from itertools import product
from typing import Iterable, Iterator, Optional, Self, Tuple
from src.battle_team import TeamBattlePosition, Teams
from src.team import Team
from src.patterns.sequential_enum import SequentialEnum
from src.technique import Technique
from src.targets import ActionTarget
from src.tem import Tem


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

class BattleField():
    def __init__(self, teams: dict[Teams, Team]) -> None:
        self.__teams = teams
        self.__battle_field: dict[Teams, dict[TeamBattlePosition, Optional[Tem]]] = {}

        # initialize battle field as empty
        # battle_handler must set the tems into the battle field
        for team_color in Teams:
            self.__battle_field[team_color] = {}
            for position in TeamBattlePosition:
                self.__battle_field[team_color][position] = None

    @property
    def teams(self) -> dict[Teams, Team]:
        return self.__teams

    def get_tem(self, team: Teams, position: TeamBattlePosition) -> Optional[Tem]:
        return self.__battle_field[team][position]

    def get_bench(self, team: Teams) -> Iterable[Tem]:
        active: list[Tem] = [tem for _, tem in self.get_active(team)]

        for tem in self.__teams[team]:
            if not tem in active:
                yield tem

    def get_active(self, team: Teams) -> Iterable[Tuple[TeamBattlePosition,Tem]]:
        for position, tem in self.__battle_field[team].items():
            if not tem is None:
                yield (position, tem)

class BattleState():
    def __init__(self, team_orange: Team, team_blue: Team):
        self.__battle_field: BattleField = BattleField({
            Teams.ORANGE: team_orange,
            Teams.BLUE: team_blue,
        })
        self.__speed_arrow: Teams = Teams.BLUE
        self.__phase: BattlePhase = BattlePhase.NOT_STARTED
        self.__reset_phase_turn()
        self.__history: dict[BattlePhase, list[TurnAction]] = {} # proper class ?
        self.clear_action_selection()

    @property
    def positions(self) -> Iterator[Tuple[Teams, TeamBattlePosition]]:
        """
        Returns all the positions that can perform an action (#TODO)
        """
        for team_color in self.__battle_field.teams:
            # TODO actually check the positions available before yielding
            for position in TeamBattlePosition:
                yield (team_color, position)

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

    def get_items(self, team: Teams) -> Iterable[Item]: #pylint: disable=unused-argument
        # TODO: implement it, one day
        return []

    def get_bench(self, team: Teams) -> Iterable[Tem]:
        return self.__battle_field.get_bench(team)

    def get_techniques(self, team: Teams, position: TeamBattlePosition) -> Iterable[Technique]:
        tem: Optional[Tem] = self.__battle_field.get_tem(team, position)

        if tem is None:
            return []

        return tem.battle_techniques

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


class Item:
    def __init__(self) -> None:
        raise NotImplementedError

    @property
    def possible_targets(self) -> Iterable[ActionTarget]:
        # TODO make it depend on the item ?
        return [
            ActionTarget.SELF,
            ActionTarget.TEAM_MATE,
            ActionTarget.OPPONENT_LEFT,
            ActionTarget.OPPONENT_RIGHT,
        ]

ActionDetail = Technique | Item | Tem

class Action(ABC):
    def __init__(
            self,
            selected_target: Optional[ActionTarget] = None,
            detail: Optional[ActionDetail] = None
    ):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        raise NotImplementedError

    @abstractmethod
    def is_compatible(self,
        self_position: TeamBattlePosition,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        """
        Checks if two actions are compatible for use in the same team.
        """

class UseTechniqueAction(Action):

    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        actions = ActionCollection()

        for tech in state.get_techniques(team, position):
            for target in tech.targets.to_action_target():
                actions.add(
                    cls(selected_target=target, detail=tech),
                    team,
                    position
                )

        return actions

class SwitchTemAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        actions = ActionCollection()

        for temtem in state.get_bench(team):
            actions.add(
                cls(selected_target=ActionTarget.SELF, detail=temtem),
                team,
                position
            )

        return actions

    @property
    def in_tem(self) -> Tem:
        raise NotImplementedError

    def is_compatible(self,
        self_position: TeamBattlePosition,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        """
        A switch action is compatible with every other action type.
        It is compatible with another switch action only if they don't switch in/out the same tem
        """
        if not isinstance(other, type(self)):
            return True

        return self_position != other_position and other.in_tem != self.in_tem

class RestAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        actions = ActionCollection()

        # TODO: check if there are any situations where a temtem can't rest
        # we are assuming they can always rest, if they are on the battlefield
        actions.add(
            cls(ActionTarget.SELF),
            team,
            position
        )

        return actions

class UseItemAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        actions = ActionCollection()

        for item in state.get_items(team):
            for target in item.possible_targets:
                actions.add(
                    cls(selected_target=target, detail=item),
                    team,
                    position
                )

        return actions

class RunAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:

        actions: ActionCollection = ActionCollection()
        actions.add(cls(), team, position)

        return actions

    def is_compatible(self,
        self_position: TeamBattlePosition,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        return True


class TeamAction:
    def __init__(self, position_action: dict[TeamBattlePosition, Action]):
        self.__position_action = position_action

    @property
    def are_actions_compatible(self) -> bool:
        if len(self.__position_action) <= 1:
            return True

        return self.__position_action[TeamBattlePosition.LEFT].is_compatible(
            TeamBattlePosition.LEFT,
            self.__position_action[TeamBattlePosition.RIGHT],
            TeamBattlePosition.RIGHT
        )

class TurnAction:
    def __init__(self, team_actions: Optional[dict[Teams, TeamAction]] = None):
        self.__team_actions: dict[Teams, TeamAction] = {} if team_actions is None else team_actions

    @property
    def is_ready(self) -> bool:
        for team in Teams:
            if not self.has_team_action(team):
                return False
        return True

    @property
    def actions(self) -> list[RunnableAction]:
        raise NotImplementedError

    def has_team_action(self, team: Teams) -> bool:
        return team in self.__team_actions

    def __str__(self) -> str:
        return self.__team_actions.__str__()

class ActionCollection():
    def __init__(self) -> None:
        self.__actions: dict[Teams, dict[TeamBattlePosition, set[Action]]] = {
            Teams.BLUE: {
                TeamBattlePosition.LEFT: set(),
                TeamBattlePosition.RIGHT: set(),
            },
            Teams.ORANGE: {
                TeamBattlePosition.LEFT: set(),
                TeamBattlePosition.RIGHT: set(),
            }
        }

    def has_actions(
            self,
            team: Optional[Teams] = None,
            position: Optional[TeamBattlePosition] = None
    ) -> bool:
        teams = [team] if team else list(Teams)
        positions = [position] if position else list(TeamBattlePosition)

        for t in teams:
            for p  in positions:
                if any(self.__actions[t][p]):
                    return True

        return False

    def get_actions(
            self,
            team: Optional[Teams] = None,
            position: Optional[TeamBattlePosition] = None
    ) -> Iterable[Action]:
        teams = [team] if team else list(Teams)
        positions = [position] if position else list(TeamBattlePosition)

        res: set[Action] = set()

        for t in teams:
            for p  in positions:
                actions = self.__actions[t][p]
                if any(actions):
                    res.union(actions)

        return res

    def add(self, action: Action, team: Teams, position: TeamBattlePosition):
        self.__actions[team][position].add(action)

    def union(self, actions: Self) -> None:
        for t in Teams:
            for p in TeamBattlePosition:
                if actions.has_actions(t, p):
                    self.__actions[t][p].union(actions.get_actions(t, p))

    def __iter__(self) -> Iterator[Tuple[Teams, TeamBattlePosition, Action]]:
        for team in Teams:
            for position in TeamBattlePosition:
                if self.has_actions(team, position):
                    for action in self.get_actions(team, position):
                        yield (team, position, action)

class TurnActionCollection():
    def __init__(self, actions: ActionCollection) -> None:
        self.__actions: ActionCollection = actions

    def __iter__(self) -> Iterator[TurnAction]:
        action_lists: Iterable[Iterable[Action]] = (
            self.__actions.get_actions(team, position)
                for team in Teams
                    for position in TeamBattlePosition
                        if self.__actions.has_actions(team, position)
        )

        possibilities = product(*action_lists)

        for possibility in possibilities:
            turn_action: dict[Teams, TeamAction] = {}
            i: int = 0
            are_actions_compatible: bool = True
            for team in Teams:
                team_action: dict[TeamBattlePosition,Action] = {}
                for position in TeamBattlePosition:
                    if self.__actions.has_actions(team, position):
                        team_action[position] = possibility[i]
                        i += 1
                turn_action[team] = TeamAction(team_action)
                are_actions_compatible = turn_action[team].are_actions_compatible

                if not are_actions_compatible:
                    break

                i += 1

            if are_actions_compatible:
                yield TurnAction(turn_action)

class RunnableAction():
    def __init__(self, action: Action, team: Teams, position: TeamBattlePosition) -> None:
        raise NotImplementedError

    @property
    def team(self) -> Teams:
        raise NotImplementedError

    @property
    def priority(self) -> int:
        raise NotImplementedError

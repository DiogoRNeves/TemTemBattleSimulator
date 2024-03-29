from __future__ import annotations
from abc import ABC, abstractmethod
from enum import auto
from itertools import product
from typing import Generator, Iterable, Iterator, Optional, Self, Tuple
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
    def __init__(self, side: Teams, possible_actions: Iterable[TeamAction]):
        self.__side = side
        self.__possible_actions = possible_actions

    @property
    def side(self) -> Teams:
        return self.__side

    @property
    def possible_actions(self) -> Iterable[TeamAction]:
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

    def set_position(self, team: Teams, position: TeamBattlePosition, index: int):
        assert 0 < index < len(self.__teams[team])
        self.__battle_field[team][position] = self.__teams[team][index]


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
        self.__turn_action: TurnAction = TurnAction()

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
        return self.__turn_action

    @property
    def phase(self) -> tuple[BattlePhase, int]:
        """
        Gets the phase and the turn on that phase we're on
        """
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
        self.__phase_turn: int = 1

    def next_turn(self) -> Tuple[BattlePhase,int]:
        self.__phase_turn += 1
        return self.phase

    def get_alive_temtems(self, team: Teams) -> Iterator[Tem]:
        for tem in self.__battle_field.teams[team]:
            if tem.is_alive:
                yield tem

    def select_action(self, action: TeamAction, team: Teams):
        self.__turn_action.add(team, action)

    def is_team_action_selected(self, team: Teams) -> bool:
        return self.__turn_action.has_team_action(team)

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

    def set_battlefield_position(self, team: Teams, position: TeamBattlePosition, index: int):
        self.__battle_field.set_position(team, position, index)

    def team_has_temtem_in_position(self, team: Teams, position: TeamBattlePosition):
        # TODO implement a battlefield that takes care of the positions
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
            selected_target: ActionTarget
    ):
        self._target = selected_target

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
    def __init__(self, selected_target: ActionTarget, technique: Technique):
        super().__init__(selected_target)
        self._technique = technique

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
                    cls(selected_target=target, technique=tech),
                    team,
                    position
                )

        return actions

    def is_compatible(self,
        self_position: TeamBattlePosition,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        """
        Using a Technique is compatible to every action
        """
        return self_position != other_position

class SwitchTemAction(Action):
    def __init__(self,
        tem_in: Tem
    ):
        super().__init__(ActionTarget.SELF)
        self.__tem_in = tem_in

    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        state: BattleState
    ) -> ActionCollection:
        actions = ActionCollection()

        for temtem in state.get_bench(team):
            actions.add(
                cls(tem_in=temtem),
                team,
                position
            )

        return actions

    @property
    def in_tem(self) -> Tem:
        return self.__tem_in

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

    def is_compatible(self,
        self_position: TeamBattlePosition,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        """
        Resting is compatible to every action
        """
        return self_position != other_position

class UseItemAction(Action):
    def __init__(self, selected_target: ActionTarget, item: Item):
        super().__init__(selected_target)
        self.__item = item

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
                    cls(selected_target=target, item=item),
                    team,
                    position
                )

        return actions

class RunAction(Action):
    def __init__(self):
        super().__init__(ActionTarget.OWN_TEAM)

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

    def __iter__(self) -> Iterator[tuple[TeamBattlePosition, Action]]:
        for position, action in self.__position_action.items():
            yield (position, action)

class TurnAction:
    def __init__(self, team_actions: Optional[dict[Teams, TeamAction]] = None):
        self.__team_actions: dict[Teams, TeamAction] = {} if team_actions is None else team_actions

    @property
    def is_ready(self) -> bool:
        for team in Teams:
            if not self.has_team_action(team):
                return False
        return True

    def to_team_action(self, team: Teams) -> TeamAction:
        return self.__team_actions[team]

    @property
    def actions(self) -> Iterator[RunnableAction]:
        for team_color, position, action in self:
            yield RunnableAction(action=action, team=team_color, position=position)

    def has_team_action(self, team: Teams) -> bool:
        return team in self.__team_actions

    def add(self, team: Teams, team_action: TeamAction):
        self.__team_actions[team] = team_action

    def __iter__(self) -> Iterator[tuple[Teams, TeamBattlePosition, Action]]:
        for team_color, team_action in self.__team_actions.items():
            for position, action in team_action:
                yield (team_color, position, action)

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
                    res = res.union(actions)

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

    def team_has_actions(self, team: Teams) -> bool:
        return self.__actions.has_actions(team=team)

    def __iter__(self) -> Iterator[TurnAction]:
        turn_action_lists: Generator[Iterable[TeamAction], None, None] = (
            self.for_team(team) for team in Teams
        )

        possibilities = product(*turn_action_lists)

        for possibility in possibilities:
            turn_action_dict: dict[Teams, TeamAction] = {}

            for team in Teams:
                turn_action_dict[team] = possibility[team.value - 1] # auto() starts on 1

            yield TurnAction(turn_action_dict)

    def for_team(self, team: Teams) -> Iterable[TeamAction]:
        # TODO we need to be more efficient. this is very slow
        # lets first generate team actions, and them combine them all later
        action_lists: Generator[Iterable[Action], None, None] = (
            self.__actions.get_actions(team, position)
                for position in TeamBattlePosition
                    if self.__actions.has_actions(team, position)
        )

        possibilities = product(*action_lists)

        for possibility in possibilities:
            i: int = 0

            team_action_dict: dict[TeamBattlePosition,Action] = {}
            for position in TeamBattlePosition:
                if self.__actions.has_actions(team, position):
                    team_action_dict[position] = possibility[i]
                i += 1
            team_action = TeamAction(team_action_dict)

            if team_action.are_actions_compatible:
                yield team_action
            else:
                break

class RunnableAction():
    def __init__(self, action: Action, team: Teams, position: TeamBattlePosition) -> None:
        raise NotImplementedError

    @property
    def team(self) -> Teams:
        raise NotImplementedError

    @property
    def priority(self) -> int:
        raise NotImplementedError

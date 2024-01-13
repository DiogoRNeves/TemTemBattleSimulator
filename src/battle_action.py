from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Iterable, Iterator, Optional, Self, Tuple
from itertools import product

from src.battle_team import TeamBattlePosition, Teams
from src.technique import Technique

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

TechOrItem = Technique | Item

class ActionTarget(Enum):
    NO_SELECTION = auto() # some techniques/items do not allow for target selection
    SELF = auto()
    TEAM_MATE = auto()
    OWN_TEAM = auto()
    OPPONENT_TEAM = auto()
    OPPONENT_LEFT = auto()
    OPPONENT_RIGHT = auto()
    ALL = auto()
    OTHERS = auto()


# class ActionType(Enum):
#     USE_TECHNIQUE = auto()
#     SWITCH = auto()
#     REST = auto()
#     USE_ITEM = auto()
#     RUN = auto()



class Action(ABC):
    def __init__(
            self,
            selected_target: Optional[ActionTarget] = None,
            detail: Optional[TechOrItem] = None
    ):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        items: Iterable[Item],
        techniques: Iterable[Technique]
    ) -> ActionCollection:
        pass

    @abstractmethod
    def is_compatible(self,
        self_position,
        other: Action,
        other_position: TeamBattlePosition
    ) -> bool:
        """
        Checks if two actions are compatible for use in the same team.
        """

class UseTechniqueAction(Action):
    pass

class SwitchTemAction(Action):
    pass

class RestAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        items: Iterable[Item],
        techniques: Iterable[Technique]
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
        items: Iterable[Item],
        techniques: Iterable[Technique]
    ) -> ActionCollection:
        actions = ActionCollection()

        for item in items:
            for target in item.possible_targets:
                actions.add(
                    cls(target, item),
                    team,
                    position
                )

        return actions

class RunAction(Action):
    @classmethod
    def get_possible_actions(cls,
        team: Teams,
        position: TeamBattlePosition,
        items: Iterable[Item],
        techniques: Iterable[Technique]
    ) -> ActionCollection:

        actions: ActionCollection = ActionCollection()
        actions.add(cls(), team, position)

        return actions

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

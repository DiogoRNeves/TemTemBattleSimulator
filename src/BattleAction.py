from __future__ import annotations
from enum import Enum, auto
from typing import Iterable, Iterator, Optional, Self

from .BattleTeam import TeamBattlePosition, Teams
from .Technique import Technique

class Item:
    pass

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


class ActionType(Enum):
    USE_TECHNIQUE = auto()
    SWITCH = auto()
    REST = auto()
    USE_ITEM = auto()
    RUN = auto()

class Action:
    def __init__(self, action_type: ActionType, selected_target: ActionTarget, detail: Optional[TechOrItem] = None):
        raise NotImplementedError
    
    @property
    def team(self) -> Teams:
        raise NotImplementedError
    
    @property
    def priority(self) -> int:
        raise NotImplementedError

class TeamAction:
    def __init__(self, position_action: dict[TeamBattlePosition, Action]):
        raise NotImplementedError

class TurnAction:
    def __init__(self, team_actions: Optional[dict[Teams, TeamAction]] = None):        
        pass
    
    @property
    def is_ready(self) -> bool:
        raise NotImplementedError 
    
    @property
    def actions(self) -> list[Action]:
        raise NotImplementedError 
    
    def has_team_action(self, team: Teams) -> bool:
        raise NotImplementedError
    
    def __str__(self) -> str:
        raise NotImplementedError 
    
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

    def has_actions(self, team: Optional[Teams] = None, position: Optional[TeamBattlePosition] = None) -> bool:                        
        teams = [team] if team else list(Teams)
        positions = [position] if position else list(TeamBattlePosition)

        for t in teams:
            for p  in positions:
                if any(self.__actions[t][p]):
                    return True

        return False

    def get_actions(self, team: Optional[Teams] = None, position: Optional[TeamBattlePosition] = None) -> Iterable[Action]:
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

    @property
    def possible_turn_actions(self) -> Iterable[TurnAction]:
        # convert the individual actions into turn actions
        raise NotImplementedError
    
    def union(self, actions: Self) -> None:
        for t in Teams:
            for p in TeamBattlePosition:
                if actions.has_actions(t, p):
                    self.__actions[t][p].union(actions.get_actions(t, p))

class TurnActionCollection():
    def __init__(self, actions: ActionCollection) -> None:
        self.__turn_actions: Iterable[TurnAction] = actions.possible_turn_actions
    
    def __iter__(self) -> Iterator[TurnAction]:
        return self.__turn_actions.__iter__()
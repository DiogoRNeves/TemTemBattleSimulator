from __future__ import annotations
from enum import Enum, auto
from typing import Iterable, Iterator

from .BattleTeam import TeamBattlePosition, Teams
from .Technique import Technique

class Item:
    pass

TI = Technique | Item | None

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
    def __init__(self, action_type: ActionType, selected_target: ActionTarget, detail: TI = None):
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
    def __init__(self, team_actions: dict[Teams, TeamAction] = {}):        
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

class TurnActionCollection():
    def __init__(self, turn_actions: Iterable[TurnAction] = []) -> None:
        self.__turn_actions: set[TurnAction] = set(turn_actions)

    def __len__(self) -> int:
        return len(self.__turn_actions)
    
    def __iter__(self) -> Iterator[TurnAction]:
        return self.__turn_actions.__iter__()

    def add(self, turn_actions: Iterable[TurnAction]) -> None:
        self.__turn_actions.union(turn_actions)
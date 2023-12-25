from __future__ import annotations
from enum import Enum, auto
from typing import Iterable, Iterator, Optional, Self

from .BattleTeam import TeamBattlePosition, Teams
from .Technique import Technique

class Item:
    pass

TechOrItem = Optional[Technique | Item]

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
    def __init__(self, action_type: ActionType, selected_target: ActionTarget, detail: TechOrItem = None):
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
        self.__actions: dict[Teams, dict[TeamBattlePosition, Iterable[Action]]] = {
            Teams.BLUE: {
                TeamBattlePosition.LEFT: set(),
                TeamBattlePosition.RIGHT: set(),
            },
            Teams.ORANGE: {
                TeamBattlePosition.LEFT: set(),
                TeamBattlePosition.RIGHT: set(),
            }
        }

    @property
    def possible_turn_actions(self) -> Iterable[TurnAction]:
        # convert the individual actions into turn actions
        raise NotImplementedError
    
    def add(self, actions: dict[Teams, dict[TeamBattlePosition, Iterable[Action]]]) -> None:
        raise NotImplementedError

class TurnActionCollection():
    def __init__(self, actions: ActionCollection) -> None:
        self.__turn_actions: Iterable[TurnAction] = actions.possible_turn_actions
    
    def __iter__(self) -> Iterator[TurnAction]:
        return self.__turn_actions.__iter__()
from enum import Enum, auto
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

class TeamAction:
    def __init__(self, position_action: dict[TeamBattlePosition, Action]):
        raise NotImplementedError

class TurnAction:
    def __init__(self, team_actions: dict[Teams, TeamAction]):
        raise NotImplementedError

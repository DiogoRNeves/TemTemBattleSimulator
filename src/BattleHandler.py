
from abc import ABC, abstractmethod
from typing import Type
from .BattleAction import ActionType
from .BattleState import BattleState
from .BattleTeam import BattleTeams, Teams
from .Team import CompetitiveTeam, PlaythroughTeam, TTeam, Team
from .patterns.Singleton import singleton


class BattleHandler(ABC):
    def __init__(self, team_class: Type[TTeam], disallowed_actions: list[ActionType] = []):
        self.__team_class = team_class
        self.__allowed_actions = [action_type for action_type in ActionType if action_type not in disallowed_actions]

    def is_valid_starting_team(self, team: Team) -> bool:
        return isinstance(team, self.__team_class)

    @abstractmethod
    def before_combat(self, teams: dict[Teams, Team]) -> BattleTeams:
        raise NotImplementedError


@singleton
class CompetitiveBattleHandler(BattleHandler):
    def __init__(self):
        super().__init__(CompetitiveTeam, [ActionType.USE_ITEM, ActionType.RUN])

class EnvironmentBattleHandler(BattleHandler, ABC):
    def __init__(self, disallowed_actions: list[ActionType] = []):
        super().__init__(PlaythroughTeam, disallowed_actions)
    
    def before_combat(self, state: BattleState) -> BattleTeams:
        raise NotImplementedError

@singleton
class TamerBattleHandler(EnvironmentBattleHandler):
    def __init__(self):
        super().__init__([ActionType.RUN])
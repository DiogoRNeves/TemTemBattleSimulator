
from abc import ABC, abstractmethod
import functools
from typing import Tuple, Type
from .BattleAction import ActionType, TeamAction
from .BattleState import BattleState, SidedBattleState
from .BattleTeam import BattleTeams, Teams
from .Team import CompetitiveTeam, PlaythroughTeam, TTeam, Team
from .patterns.Singleton import singleton
from asyncio import Task, TaskGroup


class BattleAgent(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        pass

class BattleHandler(ABC):
    def __init__(self, team_class: Type[TTeam], disallowed_actions: list[ActionType] = []):
        self.__team_class = team_class
        self.__allowed_actions = [action_type for action_type in ActionType if action_type not in disallowed_actions]
    
    async def __ask_player_for_action(self, player: BattleAgent, state: SidedBattleState) -> Tuple[TeamAction, Team]:
        return (player.choose_action(state), state.side)

    async def __ask_for_actions(self, state: BattleState, players: dict[Teams, BattleAgent]):          

        async with TaskGroup() as tg:      
            for team in Teams:
                if not state.is_team_action_selected(team):
                    tg.create_task(
                        self.__ask_player_for_action(players[team], state.for_side(team))
                    ).add_done_callback(
                        lambda context: state.select_action(*context.result())
                    )
        
        # we should have all actions in state now
        assert state.is_actions_selected, f"not all actions are registered in state: {state.selected_actions}"
        


    def __process_actions(self, state: BattleState, players: dict[Teams, BattleAgent]): 
        raise NotImplementedError       
        state.clear_action_selection()

    def is_valid_starting_team(self, team: Team) -> bool:
        return isinstance(team, self.__team_class)

    async def next(self, state: BattleState, players: dict[Teams, BattleAgent]):
        assert len(players) == len(Teams), f"teams and players must be the same size: {len(players)} players, {len(Teams)} teams"

        if state.is_actions_selected:
            await self.__ask_for_actions(state, players)
        self.__process_actions(state, players)


@singleton
class CompetitiveBattleHandler(BattleHandler):
    def __init__(self):
        super().__init__(CompetitiveTeam, [ActionType.USE_ITEM, ActionType.RUN])

class EnvironmentBattleHandler(BattleHandler, ABC):
    def __init__(self, disallowed_actions: list[ActionType] = []):
        super().__init__(PlaythroughTeam, disallowed_actions)


@singleton
class TamerBattleHandler(EnvironmentBattleHandler):
    def __init__(self):
        super().__init__([ActionType.RUN])
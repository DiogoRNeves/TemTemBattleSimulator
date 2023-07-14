
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Type

from BattleState import BattleState
from .BattleAction import Action, ActionType, TeamAction
from .BattleState import BattleState, SidedBattleState
from .BattleTeam import Teams
from .Team import CompetitiveTeam, PlaythroughTeam, TTeam, Team
from .patterns.Singleton import singleton
from asyncio import TaskGroup

class BattleActionQueue(PriorityQueue[Action]):
    
    def get(self, state: BattleState) -> Action:
        """
        Returns the next action, using the current state's speed arrow to resolve ties
        """
        candidate_action = super().get()
        result: list[Action] = []
        
        if self.queue[0].priority == candidate_action.priority:
            # grab them all
            keep = []

            # Iterate through the queue and collect items with the minimum priority
            while self.qsize() > 0 and self.queue[0].priority == candidate_action.priority:
                item = super().get()
                # if different teams, resolve the tie using state's speed_arrow
                # we need to check that teams are different because otherwise we don't switch the arrow  
                if item.team == candidate_action.team:
                    keep.append(item)
                else:
                    priority_team = state.speed_tie()
                    if priority_team == item.team:
                        keep.append(candidate_action)
                        result.append(item)
                    else:
                        keep.append(item)
                        result.append(candidate_action)

                    # put the others back in the queue
                    for a in keep:
                        self.put(a)

        else:
            result.append(candidate_action)
        
        return result[0]
    

class BattleAgent(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        pass

class BattleHandler(ABC):
    def __init__(self, team_class: Type[TTeam], disallowed_actions: list[ActionType] = []):
        self.__team_class = team_class
        self.__allowed_actions: list[ActionType] = [action_type for action_type in ActionType if action_type not in disallowed_actions]
        self.__clear_action_queue()
    
    async def __ask_player_for_action(self, player: BattleAgent, state: SidedBattleState) -> TeamAction:
        return player.choose_action(state)

    async def __ask_for_actions(self, state: BattleState, players: dict[Teams, BattleAgent]):          
        self.__generate_possible_actions(state)

        async with TaskGroup() as tg:
            for team in Teams:
                if not state.is_team_action_selected(team):
                    tg.create_task(
                        self.__ask_player_for_action(players[team], state.for_side(team))
                    ).add_done_callback(
                        lambda context: state.select_action(context.result(), team)
                    )
        
        # we should have all actions in state now
        assert state.is_actions_selected, f"not all actions are registered in state: {state.selected_actions}"
        
    def __clear_action_queue(self):
        self.__action_queue: BattleActionQueue = BattleActionQueue()

    def __process_actions(self, state: BattleState):
        # add selected actions to the queue 
        for action in state.selected_actions.actions:
            self.__action_queue.put(action)

        # process the actions
        while self.__action_queue.qsize() > 0:
            action = self.__action_queue.get(state)
            self.__execute_action(action)

        self.__end_turn(state)

    def __execute_action(self, action: Action):
        raise NotImplementedError

    def is_valid_starting_team(self, team: Team) -> bool:
        return isinstance(team, self.__team_class)

    async def next(self, state: BattleState, players: dict[Teams, BattleAgent]):
        assert len(players) == len(Teams), f"teams and players must be the same size: {len(players)} players, {len(Teams)} teams"

        if state.is_actions_selected:
            await self.__ask_for_actions(state, players)
        self.__process_actions(state)

    def __end_turn(self, state: BattleState):        
        # clear selected actions from state
        state.clear_action_selection()
        state.clear_generated_actions()

        # call end turn on child class for specific stuff
        self._end_turn(state)

    def __generate_possible_actions(self, state: BattleState):
        assert not state.is_actions_selected, "Can't generate actions when actions are already selected."
        assert state.is_actions_generated, "Can't generate actions when they are already generated"

        self._generate_possible_actions(state)

    @abstractmethod
    def _generate_possible_actions(self, state: BattleState):
        pass

    @abstractmethod
    def _end_turn(self, state: BattleState):
        pass


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

    def _generate_possible_actions(self, state: BattleState):
        pass

    def _end_turn(self, state: BattleState):
        raise NotImplementedError
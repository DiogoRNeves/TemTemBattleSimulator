from __future__ import annotations
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import Iterable, Optional, Type
from asyncio import Task, TaskGroup, run

from src.battle_agent import BattleAgent
from src.battle_action import (Action, ActionCollection, RunAction,
    TeamAction, TurnActionCollection, RunnableAction, UseItemAction)
from src.battle_state import BattleState
from src.battle_team import Teams
from src.team import CompetitiveTeam, PlaythroughTeam, Team
from src.patterns.singleton import singleton

class BattleActionQueue(PriorityQueue[RunnableAction]):

    def get(self, state: BattleState) -> RunnableAction:
        """
        Returns the next action, using the current state's speed arrow to resolve ties
        """
        candidate_action = super().get()
        result: RunnableAction = candidate_action

        if self.queue[0].priority == candidate_action.priority:
            # grab them all
            keep = []

            # Iterate through the queue and collect items with the minimum priority
            while self.qsize() > 0 and self.queue[0].priority == candidate_action.priority:
                item = super().get()
                # if different teams, resolve the tie using state's speed_arrow
                # we need to check that teams are different because otherwise we
                # don't switch the arrow
                same_team: bool = item.team == candidate_action.team
                if same_team:
                    keep_a = item
                else:
                    priority_team = state.speed_tie()
                    if priority_team == item.team:
                        keep_a, result = (candidate_action, item)
                    else:
                        keep_a, result = (item, candidate_action)

                keep.append(keep_a)

                if not same_team:
                    # this means a speed tie has been resolved, so we stop looping
                    # TODO need to check how to resolve speed ties for members of the same team
                    break

            # put the others back in the queue
            for a in keep:
                self.put(a)

        return result

class BattleHandler(ABC):
    def __init__(
            self,
            team_class: Type[Team],
            disallowed_actions: Optional[Iterable[type[Action]]] = None
    ):
        if disallowed_actions is None:
            disallowed_actions = []
        self.__team_class = team_class
        self.__allowed_actions: list[type[Action]] = [
            action_type for action_type in Action.__subclasses__()
                if action_type not in disallowed_actions
        ]
        self.__clear_action_queue()
        self._possible_actions: Optional[TurnActionCollection] = None

    @property
    def _allowed_actions(self) -> list[type[Action]]:
        return self.__allowed_actions

    async def __ask_player_for_action(
            self,
            player: BattleAgent,
            state: BattleState,
            team: Teams
    ) -> tuple[TeamAction, Teams]:
        return (player.choose_action(state.for_side(team)), team)

    async def __ask_for_actions(
            self,
            state: BattleState,
            players: dict[Teams, BattleAgent]
    ) -> list[tuple[TeamAction, Teams]]:
        self.__generate_possible_actions(state)
        tasks: list[Task[tuple[TeamAction, Teams]]] = []

        async with TaskGroup() as tg:
            for team in Teams:
                if state.team_has_actions(team) and (not state.is_team_action_selected(team)):
                    tasks.append(
                        tg.create_task(
                            self.__ask_player_for_action(players[team], state, team)
                        )
                    )

        return [t.result() for t in tasks]

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

    def __execute_action(self, action: RunnableAction):
        raise NotImplementedError

    def is_valid_starting_team(self, team: Team) -> bool:
        return isinstance(team, self.__team_class)

    def next(self, state: BattleState, players: dict[Teams, BattleAgent]):
        assert len(players) == len(Teams), \
            f"teams and players must be the same size: {len(players)} players, {len(Teams)} teams"

        if not state.is_actions_selected:
            actions = run(self.__ask_for_actions(state, players)) # asyncio.run
            for team_action, team in actions:
                state.select_action(team_action, team)
        self.__process_actions(state)

    def __end_turn(self, state: BattleState):
        # clear selected actions from state
        state.clear_action_selection()
        self._clear_generated_actions()

        # call end turn on child class for specific stuff
        self._end_turn(state)

    def _clear_generated_actions(self):
        self._possible_actions = None

    def __generate_possible_actions(self, state: BattleState):
        assert not state.is_actions_selected, \
            "Can't generate actions when actions are already selected."

        self._generate_possible_actions(state)

    def _generate_possible_actions(self, state: BattleState):
        actions: ActionCollection = ActionCollection()
        for action_type in self.__allowed_actions:
            for team, position in state.positions:
                actions_for_type: ActionCollection = \
                    action_type.get_possible_actions(
                        team,
                        position,
                        state.get_items(team),
                        state.get_techniques(team, position)
                    )

                if actions_for_type.has_actions():
                    actions.union(actions_for_type)


        self._possible_actions = TurnActionCollection(actions)


    @abstractmethod
    def _end_turn(self, state: BattleState):
        pass


@singleton
class CompetitiveBattleHandler(BattleHandler):
    def __init__(self):
        super().__init__(CompetitiveTeam, [UseItemAction, RunAction])


    def _end_turn(self, state: BattleState):
        raise NotImplementedError

@singleton
class EnvironmentBattleHandler(BattleHandler, ABC):
    def __init__(self, disallowed_actions: Optional[Iterable[type[Action]]] = None):
        super().__init__(PlaythroughTeam, disallowed_actions)

@singleton
class TamerBattleHandler(EnvironmentBattleHandler):
    def __init__(self):
        super().__init__([RunAction])

    def _end_turn(self, state: BattleState):
        raise NotImplementedError

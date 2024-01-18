
from abc import ABC, abstractmethod
import random

from src.battle_state import SidedBattleState, TeamAction

class BattleAgent(ABC):
    @abstractmethod
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        pass


class FirstActionAvailableBattleAgent(BattleAgent):
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        return next(state.possible_actions.__iter__()) # pylint:disable=unnecessary-dunder-call

class RandomBattleAgent(BattleAgent):
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        return random.choice(list(state.possible_actions))

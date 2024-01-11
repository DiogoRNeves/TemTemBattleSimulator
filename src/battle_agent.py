
from abc import ABC, abstractmethod
import random

from src.battle_action import TeamAction
from src.battle_state import SidedBattleState

class BattleAgent(ABC):
    @abstractmethod
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        pass


class FirstActionAvailableBattleAgent(BattleAgent):
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        return state.possible_actions[0]

class RandomBattleAgent(BattleAgent):
    def choose_action(self, state: SidedBattleState) -> TeamAction:
        return random.choice(state.possible_actions)

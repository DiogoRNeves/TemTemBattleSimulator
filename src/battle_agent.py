
from abc import ABC, abstractmethod
from random import Random

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
    def __init__(self, r: Random = Random()) -> None:
        super().__init__()
        self.__random = r

    def choose_action(self, state: SidedBattleState) -> TeamAction:
        i: int = self.__random.randint(0, len(state.possible_actions) - 1)
        return state.possible_actions[i]

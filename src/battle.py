from copy import deepcopy

from src.battle_team import Teams
from src.battle_handler import BattleAgent, BattleHandler
from src.battle_state import BattleResult, BattleState

class Battle():
    def __init__(self, state: BattleState, handler: BattleHandler):
        self.__state: BattleState = deepcopy(state)
        self.__handler: BattleHandler = handler

    @property
    def state(self) -> BattleState:
        return self.__state

    def run(self, players: dict[Teams, BattleAgent]) -> BattleResult:
        while not self.state.is_over:
            self.__handler.next(self.state, players)

        return self.state.result

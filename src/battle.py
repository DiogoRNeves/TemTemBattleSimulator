from copy import deepcopy

from src.battle_team import Teams
from src.battle_handler import BattleAgent, BattleHandler
from src.battle_state import BattlePhase, BattleResult, BattleState

class Battle():
    def __init__(self, state: BattleState, handler: BattleHandler):
        self.__state: BattleState = deepcopy(state)
        self.__handler: BattleHandler = handler

    @property
    def state(self) -> BattleState:
        return self.__state

    async def run(self, players: dict[Teams, BattleAgent]) -> BattleResult:
        if self.state.phase[0] == BattlePhase.NOT_STARTED:
            self.state.next_phase()

        while not self.state.is_over:
            await self.__handler.next(self.state, players)

        return self.state.result

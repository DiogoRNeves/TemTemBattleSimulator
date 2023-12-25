
from random import Random
from typing import Callable

from .BattleTeam import Teams
from .BattleHandler import BattleAgent, BattleHandler
from .BattleState import BattleResult, BattleState
from copy import deepcopy
from .Tem import Tem

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

if __name__ == '__main__':
    
    from .Team import CompetitiveTeam
    from .Tempedia import Tempedia
    from .StatsInitializer import TvsInitializer
    from .BattleHandler import TamerBattleHandler, EnvironmentBattleHandler, CompetitiveBattleHandler
    from .Stat import Stat
    from .TemTemConstants import PLAYTHROUGH_TEAM_SIZE
    from .BattleAgent import FirstActionAvailableBattleAgent, RandomBattleAgent
    from icecream import ic

    r: Random = Random(2)

    def generate_team(id_generator: Callable[[Random],int], tvs: TvsInitializer, team_size: int = PLAYTHROUGH_TEAM_SIZE) -> list[Tem]:
        t: list[Tem] = []
        for _ in range(team_size):
            id: int = id_generator(r)
            name: str = Tempedia.get_name(id)

            ic(name)

            t.append(Tem.from_competitive(id, tvs))

        return t
    
    ic('generating team spatk')
    tems_spatk = generate_team(
        Tempedia.get_random_spatk_id, 
        TvsInitializer({Stat.SPD: 500, Stat.SPATK: 500})
    )

    ic('generating team atk')
    tems_atk = generate_team(
        Tempedia.get_random_atk_id, 
        TvsInitializer({Stat.SPD: 500, Stat.ATK: 500})
    )

    s = BattleState(
        team_orange=CompetitiveTeam(tems_spatk), 
        team_blue=CompetitiveTeam(tems_atk)
    )

    b = Battle(
        state=s, 
        handler=TamerBattleHandler()
    )

    p = {
        Teams.BLUE: RandomBattleAgent(),
        Teams.ORANGE: FirstActionAvailableBattleAgent()
    }

    # this one throws a lot of NotImplementedException at the moment :-)
    result: BattleResult = b.run(p)

    ic(result)
    
    

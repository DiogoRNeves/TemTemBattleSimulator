from hypothesis import event, given, strategies as st
from src.battle_agent import BattleAgent
from src.battle_team import Teams
from src.battle import Battle
from src.battle_handler import TamerBattleHandler
from src.battle_state import BattleResult, BattleState
from src.team import PlaythroughTeam

@given(
    seed=st.random_module(),
    orange_agent_class=st.sampled_from(BattleAgent.__subclasses__()),
    blue_battle_class=st.sampled_from(BattleAgent.__subclasses__())
)
def test_ai_agent_battle_ends(seed, orange_agent_class, blue_battle_class):
    event(seed)
    s = BattleState(
        team_orange=PlaythroughTeam.get_random(),
        team_blue=PlaythroughTeam.get_random()
    )

    b = Battle(
        state=s,
        handler=TamerBattleHandler()
    )

    p: dict[Teams, BattleAgent] = {
        Teams.BLUE: orange_agent_class(),
        Teams.ORANGE: blue_battle_class()
    }

    # this one throws a lot of NotImplementedException at the moment :-)
    result: BattleResult = b.run(p)
    assert not result is None

import json
import random
from typing import Any, Final

from collections.abc import Iterable
from typing_extensions import TypedDict, NotRequired

from src.tem_stat import Stat
from src.team import PlaythroughTeam
from src.tem import Tem
from src.tempedia import Tempedia
import src.tem_tem_constants as TemTemConstants

MIN_AI_SVS: Final[int] = TemTemConstants.MIN_SV  # + 24


class ConfigTem(TypedDict):
    name: str
    level: int
    techniques: list[str]
    svs: NotRequired[list[int]]
    tvs: NotRequired[list[int]]
    nickname: NotRequired[str]


def get_json(path: str) -> Any:
    with open(path, encoding="utf8") as file:
        # Load its content and make a new dictionary
        return json.load(file)


# import configs
CONFIGS_PATH: Final[str] = "./nuzlocke_helper_configs"

my_team_config: list[ConfigTem] = get_json(CONFIGS_PATH + "/my_team.json")
assert isinstance(my_team_config, Iterable), "json for my_teams must be an Iterable."
opponent_tems_config: list[ConfigTem] = get_json(CONFIGS_PATH + "/opponent_tems.json")
assert isinstance(
    opponent_tems_config, Iterable
), "json for opponent_tems must be an Iterable."


my_team = PlaythroughTeam(
    [
        Tem.from_data(
            name=d["name"],
            svs=d.get("svs", [
                random.randint(TemTemConstants.MIN_SV,TemTemConstants.MAX_SV)
                    for _ in range(len(Stat))
                ]
            ),
            tvs=d.get("tvs", [0] * len(Stat)),
            level=d["level"],
            battle_techniques=d["techniques"],
            nickname=d.get("nickname", ""),
        )
        for d in my_team_config
    ]
)

# TODO migrate to arguably
if __name__ == "__main__":
    from icecream import ic
    import argparse

    def custom_opponent_tem(val: str) -> ConfigTem:
        t = val.split(",")
        if t[0].lower() not in map(str.lower,Tempedia.get_names()):
            raise ValueError(f"Tem Species does not exist: {t[0]}")
        if len(t) != 2:
            raise TypeError(
                f"CustomTem must have a format of [TemSpeciesName],[level]: {val=}"
            )
        return {"name": t[0], "level": int(t[1]), "techniques": []}

    def dojo_leader_tems(val: str) -> list[ConfigTem]:
        raise NotImplementedError

    my_tem_names = [t.nickname if t.has_nickname else t.species_name for t in my_team]
    opponent_tem_names = [t["name"] for t in opponent_tems_config]

    parser = argparse.ArgumentParser(
        description="Provides damage calculations for TemTem."
    )

    parser.add_argument(
        "--my_tems",
        required=False,
        choices=list(map(str.lower, my_tem_names)),
        type=str.lower,
        default=my_tem_names,
        nargs="+",
        help="The list of my tems (from my_team.json) to do the calculations on.",
    )
    opponents_group = parser.add_mutually_exclusive_group()
    opponents_group.add_argument(
        "--opponent_tems",
        required=False,
        choices=list(map(str.lower, opponent_tem_names)),
        type=str.lower,
        default=opponent_tem_names,
        nargs="+",
        help="The list of opponent tems (from opponent_tems.json) to do the calculations on.",
    )
    opponents_group.add_argument(
        "--custom_opponent_tems",
        required=False,
        type=custom_opponent_tem,
        nargs="+",
        help="A list of custom opponent tems, having the form [TemSpeciesName],[level]. " + \
            "For example: Sparzy,16",
    )
    opponents_group.add_argument(
        "--dojo_leader",
        required=False,
        type=dojo_leader_tems,
        nargs="+",
        help="The name of the dojo leader, followed by the desired tems, if any.",
    )

    args = parser.parse_args()

    # filter my tems
    my_iterable_tems = [my_team(name) for name in args.my_tems]

    # properly set opponent's tems
    max_sv_tems = []
    min_sv_tems = []

    opponent_tems = (
        [t for t in opponent_tems_config if t["name"].lower() in args.opponent_tems]
        if args.custom_opponent_tems is None
        else args.custom_opponent_tems
    )

    ic(opponent_tems)

    for d in opponent_tems:
        max_sv_tems.append(
            Tem.from_data(
                name=d["name"],
                level=d["level"],
                svs=[TemTemConstants.MAX_SV] * len(Stat),
                battle_techniques=d["techniques"],
            )
        )

        min_sv_tems.append(
            Tem.from_data(
                name=d["name"],
                level=d["level"],
                svs=[MIN_AI_SVS] * len(Stat),
                battle_techniques=d["techniques"],
            )
        )

    opponent_teams = {
        "max_svs": PlaythroughTeam(max_sv_tems),
        "min_svs": PlaythroughTeam(min_sv_tems),
    }

    max_sv_opponents = opponent_teams["max_svs"]
    min_sv_opponents = opponent_teams["min_svs"]

    for my_tem in my_iterable_tems:
        print(my_tem)

        for opponent_max_sv in opponent_teams["max_svs"]:
            opponent_min_sv = min_sv_opponents(opponent_max_sv.species_name)

            assert (
                opponent_max_sv.display_name == opponent_min_sv.display_name
            ), "max_sv and min_sv tems must have the same display name: " + \
                f"{opponent_min_sv.display_name=} {opponent_max_sv.display_name=}"
            attacker_text = f"\t-> {opponent_max_sv.display_name}"
            print(attacker_text)

            for technique in my_tem.battle_techniques:
                # calculate attacks
                min_dmg_percent = (
                    my_tem.calculate_atacking_damage(technique, opponent_max_sv)
                    / opponent_max_sv.stats[Stat.HP]
                )  # min damage is done to max_svs oponent

                # calculate the range by using the min stats opponent
                max_dmg_percent = (
                    my_tem.calculate_atacking_damage(
                        technique,
                        opponent_min_sv,
                    )
                    / opponent_min_sv.stats[Stat.HP]
                )

                assert (
                    min_dmg_percent <= max_dmg_percent
                ), "min damage must be lower than max damage: " + \
                    f"{min_dmg_percent=} {max_dmg_percent=}"

                # to % string
                min_dmg_percent_str = f"{min_dmg_percent * 100} %"
                max_dmg_percent_str = f"{max_dmg_percent * 100} %"

                attacks_text = (
                    f"\t\t[{technique}] = {min_dmg_percent_str} - {max_dmg_percent_str}"
                )

                print(attacks_text)

            print("\n")

            defender_text = f"\t<- {opponent_max_sv.display_name}"
            print(defender_text)

            for technique in opponent_max_sv.battle_techniques:
                # calculate defenses
                dmg = my_tem.calculate_defensive_damage(
                    technique, opponent_max_sv
                )  # max damage is done by max_svs oponent
                defends_text = f"\t\t[{technique}] <= {dmg}"

                print(defends_text)

            print("\n")

        print("\n\n")

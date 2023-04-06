import json
from typing import Any, Final

from collections.abc import Iterable

from Stat import Stat
from Team import PlaythroughTeam
from Technique import Technique
from Tem import Tem
import TemTemConstants

MIN_AI_SVS: Final[int] = TemTemConstants.MIN_SV # + 24 

def get_json(path: str) -> Any:
    with open(path, encoding="utf8") as file:
        # Load its content and make a new dictionary
        return json.load(file)


# import configs
CONFIGS_PATH: Final[str] = "./nuzlocke_helper_configs"

my_team_config = get_json(CONFIGS_PATH + "/my_team.json")
assert isinstance(my_team_config, Iterable), f"json for my_teams must be an Iterable."
opponent_tems_config = get_json(CONFIGS_PATH + "/opponent_tems.json")
assert isinstance(
    opponent_tems_config, Iterable
), f"json for opponent_tems must be an Iterable."


my_team = PlaythroughTeam(
    [
        Tem.from_data(
            name=d["name"],
            svs=d["svs"],
            tvs=d["tvs"],
            level=d["level"],
            battle_techniques=d["techniques"],
            nickname=d["nickname"],
        )
        for d in my_team_config
    ]
)


max_sv_tems = []
min_sv_tems = []

for d in opponent_tems_config:
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

if __name__ == "__main__":
    from icecream import ic

    max_sv_opponents = opponent_teams["max_svs"]
    min_sv_opponents = opponent_teams["min_svs"]

    for my_tem in my_team:
        ic(my_tem.display_name)

        max_guaranteed_damage_inflicted = {"damage": -1, "target": "", "technique": ""}
        max_damage_taken = {"damage": -1, "attacker": "", "technique": ""}
        for opponent_max_sv in max_sv_opponents:
            opponent_min_sv = min_sv_opponents(opponent_max_sv.species_name)
            
            assert opponent_max_sv.display_name == opponent_min_sv.display_name, f"max_sv and min_sv tems must have the same display name: {opponent_min_sv.display_name=} {opponent_max_sv.display_name=}"
            
            local_max_guaranteed_damage_inflicted = {
                "damage": -1,
                "target": "",
                "technique": "",
            }
            local_max_damage_taken = {"damage": -1, "attacker": "", "technique": ""}

            for technique in my_tem.battle_techniques:
                # calculate attacks
                dmg = (
                    my_tem.calculate_atacking_damage(technique, opponent_max_sv)
                    / opponent_max_sv.stats[Stat.HP]
                )  # min damage is done to max_svs oponent
                if dmg > local_max_guaranteed_damage_inflicted["damage"]:
                    local_max_guaranteed_damage_inflicted["damage"] = dmg
                    local_max_guaranteed_damage_inflicted[
                        "target"
                    ] = opponent_max_sv.display_name
                    local_max_guaranteed_damage_inflicted["technique"] = technique.name

                # calculate the range by using the min stats opponent
                min_dmg_percent = local_max_guaranteed_damage_inflicted["damage"]
                max_dmg_percent = (
                    my_tem.calculate_atacking_damage(
                        Technique(local_max_guaranteed_damage_inflicted["technique"]),
                        opponent_min_sv,
                    )
                    / opponent_min_sv.stats[Stat.HP]
                )

                assert min_dmg_percent <= max_dmg_percent, f"min damage must be lower than max damage: {min_dmg_percent=} {max_dmg_percent=}"

                # to % string
                local_max_guaranteed_damage_inflicted[
                    "min_dmg_%"
                ] = f"{min_dmg_percent * 100} %"
                local_max_guaranteed_damage_inflicted[
                    "max_dmg_%"
                ] = f"{max_dmg_percent * 100} %"

            if (
                local_max_guaranteed_damage_inflicted["damage"]
                > max_guaranteed_damage_inflicted["damage"]
            ):
                max_guaranteed_damage_inflicted[
                    "damage"
                ] = local_max_guaranteed_damage_inflicted["damage"]
                max_guaranteed_damage_inflicted[
                    "target"
                ] = local_max_guaranteed_damage_inflicted["target"]
                max_guaranteed_damage_inflicted[
                    "technique"
                ] = local_max_guaranteed_damage_inflicted["technique"]
                max_guaranteed_damage_inflicted[
                    "max_dmg_%"
                ] = local_max_guaranteed_damage_inflicted["max_dmg_%"]
                max_guaranteed_damage_inflicted[
                    "min_dmg_%"
                ] = local_max_guaranteed_damage_inflicted["min_dmg_%"]

            for technique in opponent_max_sv.battle_techniques:
                # calculate defenses
                dmg = my_tem.calculate_defensive_damage(
                    technique, opponent_max_sv
                )  # max damage is done by max_svs oponent
                if dmg > local_max_damage_taken["damage"]:
                    dmg_percent = dmg / my_tem.stats[Stat.HP]
                    local_max_damage_taken["damage"] = dmg
                    local_max_damage_taken["attacker"] = opponent_max_sv.display_name
                    local_max_damage_taken["technique"] = technique.name
                    local_max_damage_taken["dmg_%"] = f"{dmg_percent * 100} %"

            if local_max_damage_taken["damage"] > max_damage_taken["damage"]:
                max_damage_taken["damage"] = local_max_damage_taken["damage"]
                max_damage_taken["attacker"] = local_max_damage_taken["attacker"]
                max_damage_taken["technique"] = local_max_damage_taken["technique"]
                max_damage_taken["dmg_%"] = local_max_damage_taken["dmg_%"]

            del local_max_damage_taken["attacker"]
            del local_max_guaranteed_damage_inflicted["target"]
            del local_max_guaranteed_damage_inflicted["damage"]

            ic(
                opponent_max_sv.display_name,
                local_max_guaranteed_damage_inflicted,
                local_max_damage_taken,
            )

        del max_guaranteed_damage_inflicted["damage"]

        ic(max_guaranteed_damage_inflicted, max_damage_taken)
        print("\n\n")



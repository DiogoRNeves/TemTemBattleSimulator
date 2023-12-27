
from typing_extensions import TypedDict, NotRequired

TechniqueJson = TypedDict("TechniqueJson",
    {
        "name": str,
        "type": str,
        "class": str,
        "damage": int,
        "staminaCost": int,
        "hold": int,
        "priority": str,
        "synergy": str,
        "targets": str,
        "effectText": str,
        "synergyEffects": list # TODO: check what is inside the list
    }
)

TemTemStatsJson = TypedDict(
    "TemTemStatsJson",
    {
        "hp": int,
        "sta": int,
        "spd": int,
        "atk": int,
        "def": int,
        "spatk": int,
        "spdef": int,
        "total": int
    }
)

class SimplifiedTechnique(TypedDict):
    name: str
    source: str
    levels: NotRequired[int]

class TemTemJson(TypedDict):
    number: int
    name: str
    types: list[str]
    stats: TemTemStatsJson
    traits: list[str]
    techniques: list[SimplifiedTechnique]

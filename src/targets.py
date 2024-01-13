from __future__ import annotations

from enum import Enum, auto
from typing import Final, Iterable


class ActionTarget(Enum):
    NO_SELECTION = auto() # some techniques/items do not allow for target selection
    SELF = auto()
    TEAM_MATE = auto()
    OWN_TEAM = auto()
    OPPONENT_TEAM = auto()
    OPPONENT_LEFT = auto()
    OPPONENT_RIGHT = auto()
    ALL = auto()
    OTHERS = auto()


# ic| k: 'targets'
#     set([t[k] for t in _techniques.values()]): {'All',
#                                                 'All Other Temtem',
#                                                 'Other Team or Ally',
#                                                 'Self',
#                                                 'Single Other Target',
#                                                 'Single Target',
#                                                 'Single Team'}

class TechniqueTargets(Enum):
    """
    An enumeration representing the possible targets of a technique.

    Attributes:
        ALL (TechniqueTargets): All temtem, including allies and foes.
        ALL_OTHER_TEMTEM (TechniqueTargets): All temtem other than the user.
        OTHER_TEAM_OR_ALLY (TechniqueTargets): An ally or a foe.
        SELF (TechniqueTargets): The user of the technique.
        SINGLE_OTHER_TARGET (TechniqueTargets): A single temtem other than the user.
        SINGLE_TARGET (TechniqueTargets): A single temtem, including allies and foes.
        SINGLE_TEAM (TechniqueTargets): All temtem on the user's team.
    """
    ALL = auto()
    ALL_OTHER_TEMTEM = auto()
    OTHER_TEAM_OR_ALLY = auto()
    SELF = auto()
    SINGLE_OTHER_TARGET = auto()
    SINGLE_TARGET = auto()
    SINGLE_TEAM = auto()

    @staticmethod
    def from_string(targets: str) -> TechniqueTargets:
        """Returns a TechniqueTargets instance based on the given string.

        Args:
        - targets (str): The string to match to a TechniqueTargets instance.

        Returns:
        - TechniqueTargets: The corresponding TechniqueTargets instance.

        """
        return TechniqueTargets[targets.replace(" ", "_").upper()]

    def to_action_target(self) -> Iterable[ActionTarget]:
        return TECHNIQUE_TO_ACTION[self]

TECHNIQUE_TO_ACTION: Final[dict[TechniqueTargets, list[ActionTarget]]] = {
    TechniqueTargets.ALL: [ActionTarget.ALL],
    TechniqueTargets.ALL_OTHER_TEMTEM: [ActionTarget.OTHERS],
    TechniqueTargets.OTHER_TEAM_OR_ALLY: [ActionTarget.OPPONENT_TEAM, ActionTarget.TEAM_MATE],
    TechniqueTargets.SINGLE_OTHER_TARGET: [
        ActionTarget.TEAM_MATE, ActionTarget.OPPONENT_RIGHT, ActionTarget.OPPONENT_LEFT
    ],
    TechniqueTargets.SELF: [ActionTarget.SELF],
    TechniqueTargets.SINGLE_TARGET: [
        ActionTarget.SELF, ActionTarget.TEAM_MATE,
        ActionTarget.OPPONENT_RIGHT, ActionTarget.OPPONENT_LEFT
    ],
    TechniqueTargets.SINGLE_TEAM: [
        ActionTarget.OWN_TEAM, ActionTarget.OPPONENT_TEAM
    ]
}

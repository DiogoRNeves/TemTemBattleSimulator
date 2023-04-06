from abc import ABC
import random
from typing import Callable, Final, Iterator
from Technique import Technique
import TemTemConstants


class TechniqueSet(ABC):
    def __init__(self, techniques: list[str], max_set_size: int):
        techniques_set = set(techniques)  # no dupes
        assert (
            len(techniques_set) <= max_set_size
        ), f"Too many techniques: {len(techniques_set)=} {max_set_size=}"
        assert (
            len(techniques_set) > 1
        ), f"Must pass in at least one technique: {len(techniques_set)=} {techniques_set=}"
        self.__MAX_SET_SIZE: Final[int] = max_set_size
        self._techniques: list[Technique] = [Technique(t) for t in techniques_set]

    @property
    def names(self) -> list[str]:
        return [t.name for t in self]

    def add(self, technique: str):
        assert (
            len(self) < self.__MAX_SET_SIZE
        ), f"Can't add technique, set is already full: {len(self)=} {self.__MAX_SET_SIZE=}"
        assert (
            technique not in self.names
        ), f"Can't add technique - it already exists in the set: {technique=} {self.names=}"
        self._techniques.append(Technique(technique))

    def remove(self, technique: str):
        assert (
            technique in self.names
        ), f"Can't remove technique - it doesn't exist in the set: {technique=} {self.names=}"
        assert (
            len(self) > 1
        ), f"Can't remove technique - there's only one technique in the set. {self.names=}"
        # self._techniques.remove(Technique(technique))
        # self._techniques = list(filter(lambda t: t.name != technique, self._techniques))
        self._techniques = [
            t for t in self._techniques if t.name != technique
        ]  # this will mess up the order, but looks simpler and more efficient

    def replace(self, old_technique: str, new_technique: str):
        """Replaces old_technique with new_technique, but not in the same order"""
        self.remove(old_technique)
        self.add(new_technique)

    def get_random_techniques(
        self, number_of_techniques, fltr: Callable[[Technique], bool] = lambda a: True
    ) -> list[Technique]:
        """
        Gets random techniques from the set, with an optional filter.
        If more than the available number of available techniques is requested, all techniques will be returned.
        """
        assert (
            number_of_techniques > 0
        ), f"You must request at least one technique: {number_of_techniques=}"
        n = min(len(self), number_of_techniques)  # ensures proper result

        if n == len(self):
            return self._techniques.copy()

        return random.sample(list(filter(fltr, self._techniques)), n)

    def get_random_technique(
        self, fltr: Callable[[Technique], bool] = lambda a: True
    ) -> Technique:
        return self.get_random_techniques(1, fltr)[0]

    def __len__(self) -> int:
        return len(self._techniques)

    def __iter__(self) -> Iterator[Technique]:
        return self._techniques.__iter__()


class BattleTechniques(TechniqueSet):
    def __init__(self, techniques: list[str]):
        super().__init__(techniques, TemTemConstants.NUMBER_OF_BATTLE_TECHNIQUES)


class LearnableTechniques(TechniqueSet):
    def __init__(self, techniques: list[str]):
        super().__init__(techniques, 999)

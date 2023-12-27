from enum import Enum
from typing import TypeVar

SE = TypeVar('SE', bound='SequentialEnum')

class SequentialEnum(Enum):
    def next(self: SE, loop: bool = True) -> SE:
        cls = self.__class__
        members: list[SE] = list(cls.__members__.values())
        index = members.index(self) + 1
        if index >= len(members):
            if loop:
                # to cycle around
                index = 0
            else:
                raise StopIteration('end of enumeration reached')
        return members[index]

    def prev(self: SE, loop: bool = True) -> SE:
        cls = self.__class__
        members: list[SE] = list(cls)
        index = members.index(self) - 1
        if index < 0:
            if loop:
                # to cycle around
                index = len(members) - 1
            else:
                raise StopIteration('beginning of enumeration reached')
        return members[index]

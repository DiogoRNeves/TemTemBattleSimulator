import threading
from typing import Type, TypeVar

T = TypeVar('T')

# https://old.reddit.com/r/Python/comments/2qkwgh/class_to_enforce_singleton_pattern_on_subclasses/
def singleton(theclass: Type[T]) -> Type[T]:
    # Assumes that theclass doesn't define a __new__ method.
    # Defining __init__ is okay though.
    object.__setattr__(theclass, 'singleton_instance', None)
    lock = threading.Lock()
    def __new__(cls: Type[T], *args, **kwargs) -> T:
        with lock:
            if cls.singleton_instance is None:
                if theclass.__base__ is object:
                    obj = super(theclass, cls).__new__(cls, None)
                else:
                    obj = super(theclass, cls).__new__(cls, *args, **kwargs)
                cls.singleton_instance = obj
            return cls.singleton_instance
    theclass.__new__ = __new__
    return theclass

import threading
from typing import Type

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# https://old.reddit.com/r/Python/comments/2qkwgh/class_to_enforce_singleton_pattern_on_subclasses/
def singleton(theclass: Type[object]) -> Type[object]:
    # Assumes that theclass doesn't define a __new__ method.
    # Defining __init__ is okay though.
    theclass.instance = None
    lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        with lock:
            if cls.instance is None:
                if theclass.__base__ is object:
                    obj = super(theclass, cls).__new__(cls, None)
                else:
                    obj = super(theclass, cls).__new__(cls, *args, **kwargs)
                cls.instance = obj
            return cls.instance
    theclass.__new__ = __new__
    return theclass

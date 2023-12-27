import threading

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# https://old.reddit.com/r/Python/comments/2qkwgh/class_to_enforce_singleton_pattern_on_subclasses/
def singleton(theclass):
    # Assumes that theclass doesn't define a __new__ method.
    # Defining __init__ is okay though.
    theclass._instance = None
    lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        with lock:
            if cls._instance is None:
                if theclass.__base__ is object:
                    obj = super(theclass, cls).__new__(cls, None)
                else:
                    obj = super(theclass, cls).__new__(cls, *args, **kwargs)
                cls._instance = obj
            return cls._instance
    theclass.__new__ = __new__
    return theclass

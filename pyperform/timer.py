__author__ = 'calvin'

from time import time
from .tools import convert_time_units

timer_format = "{name}: {time}"

def timer(func):
    def _timed_function(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(timer_format.format(name=func.__name__, time=convert_time_units(t2-t1)))
        return result

    _timed_function.__name__ = "_timed_{}".format(func.__name__)

    return _timed_function

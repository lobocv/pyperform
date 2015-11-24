__author__ = 'calvin'

from time import time

from .tools import convert_time_units

timer_format = "{name}: recent: {recent_time} average: {avg_time}"


def timer(func):
    def _timed_function(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        delta = t2-t1
        _timed_function._total_time += delta
        _timed_function._call_count += 1
        _timed_function._average_time = convert_time_units(_timed_function._total_time / _timed_function._call_count)
        print(timer_format.format(name=func.__name__, recent_time=convert_time_units(delta), avg_time=_timed_function._average_time))
        return result

    _timed_function._total_time = 0
    _timed_function._call_count = 0
    _timed_function.__name__ = "_timed_{}".format(func.__name__)

    return _timed_function

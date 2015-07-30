__author__ = 'calvin'

from time import time
from .tools import convert_time_units

timer_format = "{name}: {time}"

#
# def timer(func):
#
#     def _timed_function(*args, **kwargs):
#         t1 = time()
#         result = func(*args, **kwargs)
#         t2 = time()
#         print(timer_format.format(name=func.__name__, time=convert_time_units(t2-t1)))
#         return result
#
#     _timed_function.__name__ = "_timed_{}".format(func.__name__)
#
#     return _timed_function
#
__author__ = 'calvin'

from time import time
from .tools import convert_time_units


class Timer(object):

    timer_format = "{func.__name__}: This call: {time}"
    timer_average_format = "{func.__name__}: This call: {time}   Average: {avg}"

    def __init__(self, N_average=1):
        # self.func = func
        self.n_average = N_average
        self.call_count = 0
        self.t_sum = 0
        # self.wrapper = self.average_timed_function if self.n_average > 1 else self.timed_function

    def __call__(self, func):
        self.func = func
        self.wrapper = self.average_timed_function if self.n_average > 1 else self.timed_function
        return self.wrapper

    def average_timed_function(self, *args, **kwargs):
        t1 = time()
        result = self.func(*args, **kwargs)
        t2 = time()
        delta = t2 - t1
        self.t_sum += delta
        self.call_count += 1
        print(Timer.timer_average_format.format(func=self.func, time=convert_time_units(delta), avg=convert_time_units(self.t_sum/self.call_count)))
        return result

    def timed_function(self, *args, **kwargs):
        t1 = time()
        result = self.func(self, *args, **kwargs)
        t2 = time()
        print(Timer.timer_format.format(func=self.func, time=convert_time_units(t2-t1)))
        return result

    @classmethod
    def create_timer(cls, func=None, N_average=1):
        t = cls(func, N_average=N_average)
        # t.timed_function.__name__ = "_timed_{}".format(func.__name__)

        return t.timed_function


timer = Timer

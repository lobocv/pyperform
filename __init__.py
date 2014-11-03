__author__ = 'Calvin'
import inspect
import timeit
import StringIO
from math import log10

def convert_time_units(t):
    # Convert into reasonable time units
    order = log10(t)
    if -6 < order < -3:
        time_units = 'us'
        factor = 1000000
    elif -3 <= order < -1:
        time_units = 'ms'
        factor = 1000.
    elif -1 <= order:
        time_units = 's'
        factor = 1
    return "{:.3f} {}".format(factor * t, time_units)


class PerformanceTest(object):
    timeit_repeat = 3
    timeit_number = 10000

    def __init__(self, *func_args, **func_kwargs):
        self._func_args = func_args
        self._func_kwargs = func_kwargs

    def __call__(self, func):
        src = inspect.getsource(func)
        self.func = func
        self.func_src = src[src.index('\n') + 1:]

        self.log = log = StringIO.StringIO()
        log.write(self.func_src)

        # Create the function call statment as a string
        call = "{0}(*{1}, **{2})".format(func.__name__, self._func_args, self._func_kwargs)
        self._timer = timeit.Timer(stmt=call, setup=self.func_src)
        trials = self._timer.repeat(self.timeit_repeat, self.timeit_number)

        self.time_avg_seconds = sum(trials) / len(trials)

        # Convert into reasonable time units

        time_avg = convert_time_units(self.time_avg_seconds)
        log.write("\nAverage time: {0} \n".format(time_avg))
        print log.getvalue()

        return func


class PerformanceComparison(PerformanceTest):
    groups = {}

    def __init__(self, group, *func_args, **func_kwargs):
        self.group = group
        if group not in self.groups:
            self.groups[group] = []
        self._func_args = func_args
        self._func_kwargs = func_kwargs

    def __call__(self, func):
        super(PerformanceComparison, self).__call__(func)
        self.groups[self.group].append(self)
        return func

    @staticmethod
    def summarize(group, fs=None):
        tests = PerformanceComparison.groups[group]
        times = [test.time_avg_seconds for test in tests]
        # Find the fastest test
        fastest_time = min(times)
        index = times.index(fastest_time)
        fastest_test = tests[index]
        # Find the slowest test
        slowest_time = max(times)
        index = times.index(slowest_time)
        slowest_test = tests[index]

        time_ratios = [test.time_avg_seconds / fastest_time for test in tests]

        log = StringIO.StringIO()
        log.write('Summary\n')
        log.write('----------------------------------\n')
        log.write('Fastest function: \t {} \t {}\n'.format(fastest_test.func.__name__, convert_time_units(fastest_time)))
        log.write('Slowest function: \t {} \t {}\n'.format(slowest_test.func.__name__, convert_time_units(slowest_time)))
        log.write('----------------------------------\n')

        for test in tests:
            log.write(test.log.getvalue())
            log.write('----------------------------------\n')

        if fs:
            fs.write(log.getvalue())
        else:
            print log.getvalue()

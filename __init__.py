__author__ = 'Calvin'
import inspect
import timeit
import StringIO
from types import FunctionType
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


def globalize_indentation(src):
    # Strip the indentation level so the code runs in the global scope
    lines = src.splitlines()
    indent = len(lines[0]) - len(lines[0].strip(' '))
    func_src = ''
    for ii, l in enumerate(src.splitlines()):
        line = l[indent:]
        func_src += line + '\n'

def remove_decorators(src):
    # Remove decorators from the source code
    src_lines = src.splitlines()
    for n, line in enumerate(src_lines):
        if 'Benchmark' in line:
            del src_lines[n]
    setup_src = '\n'.join(src_lines)

    return setup_src


class Benchmark(object):
    timeit_repeat = 3
    timeit_number = 10000

    def __init__(self, setup=None, largs=None, kwargs=None):
        self.setup = setup
        if largs is not None and type(largs) is tuple:
            self._args = largs
        else:
            self._args = ()
        self._kwargs = kwargs.copy() if kwargs is not None else {}
        self.setup_src = ''
        self.callable = None
        self._is_function = None
        self.log = StringIO.StringIO()
        self.time_avg_seconds = None

    def __call__(self, caller):
        src = inspect.getsource(caller)
        self.callable = caller
        self._is_function = isinstance(caller, FunctionType)

        if self._is_function:
            setup_src = src[src.index('\n') + 1:]
        else:
            setup_src = src

        # Strip the indentation level so the code runs in the global scope
        lines = setup_src.splitlines()
        indent = len(lines[0]) - len(lines[0].strip(' '))
        src_lines = src.splitlines()
        self._is_bound_function = 'def' in src_lines[1] and 'self' in src_lines[1]
        # if self._is_bound_function..:
        #     self.stmt = "{0}(self, *{1}, **{2})".format(caller.__name__, self._args, self._kwargs)
        # else:
        self.stmt = "{0}(*{1}, **{2})".format(caller.__name__, self._args, self._kwargs)

        setup_src = ''
        for ii, l in enumerate(src_lines):
            line = l[indent:]
            setup_src += line + '\n'

        if callable(self.setup):
            setup_func = inspect.getsource(self.setup)
            setup_src = setup_func[setup_func.index('\n') + 1:]
            setup = '\n'.join([l.strip() for l in setup_src.splitlines()])
            setup += '\n\n' + setup_src
            setup_src = setup
        else:
            setup_src = setup_src

        self.setup_src = remove_decorators(setup_src)

    def run_timeit(self, stmt, setup):
        # Create the function call statment as a string
        # call = "{0}(*{1}, **{2})".format(self.callable.__name__, self._args, self._kwargs)
        _timer = timeit.Timer(stmt=stmt, setup=setup)
        trials = _timer.repeat(self.timeit_repeat, self.timeit_number)

        self.time_avg_seconds = sum(trials) / len(trials)

        # Convert into reasonable time units
        time_avg = convert_time_units(self.time_avg_seconds)

        return time_avg

class BenchmarkedClass(Benchmark):
    bound_functions = {}

    def __init__(self, setup=None, cls_args=None, cls_kwargs=None):
        self.setup = setup
        if cls_args is not None and type(cls_args) is tuple:
            self._args = cls_args
        else:
            self._args = (cls_args, )
        self._kwargs = cls_kwargs.copy() if cls_kwargs is not None else {}
        self._src = ''
        self.callable = None


    def __call__(self, cls):
        super(BenchmarkedClass, self).__call__(cls)
        setup_src = self.setup_src
        setup_src += '\ninstance = {}'.format(self.stmt)

        for p in self.bound_functions[cls.__name__]:
            stmt = "instance.{}".format(p.stmt)
            time_avg = self.run_timeit(stmt, setup_src)
            print time_avg

        return cls

class BenchmarkedFunction(Benchmark):

    def __call__(self, caller):
        super(BenchmarkedFunction, self).__call__(caller)

        log = self.log
        log.write(self.setup_src)
        if not self._is_bound_function:
            time_avg = self.run_timeit(self.stmt)
            log.write("\nAverage time: {0} \n".format(time_avg))
            print log.getvalue()

        return caller


class ComparisonBenchmark(BenchmarkedFunction):
    groups = {}

    def __init__(self, group, classname=None, setup=None, *largs, **kwargs):
        super(ComparisonBenchmark, self).__init__(setup=setup, *largs, **kwargs)
        self.group = group
        self.classname = classname
        if group not in self.groups:
            self.groups[group] = []

    def __call__(self, caller):
        super(ComparisonBenchmark, self).__call__(caller)
        self.groups[self.group].append(self)
        if self._is_bound_function:
            try:
                BenchmarkedClass.bound_functions[self.classname].append(self)
            except KeyError:
                BenchmarkedClass.bound_functions[self.classname] = [self]
        return caller

    @staticmethod
    def summarize(group, fs=None):
        tests = sorted(ComparisonBenchmark.groups[group], key=lambda t: getattr(t, 'time_avg_seconds'))
        log = StringIO.StringIO()
        log.write('Summary\n')

        fmt = "{0: <20} {1: <20} {2: <20}\n"
        log.write('{0:-<60} \n'.format(''))
        log.write(fmt.format('Function Name', 'Time', 'Fraction of fastest'))
        for t in tests:
            log.write(fmt.format(t.callable.__name__,
                                 convert_time_units(t.time_avg_seconds),
                                 "{:.3f}".format(tests[0].time_avg_seconds / t.time_avg_seconds)))
        log.write('{0:-<60} \n'.format(''))

        for test in tests:
            log.write(test.log.getvalue())
            log.write('{0:-<60} \n'.format(''))

        if fs:
            fs.write(log.getvalue())
        else:
            print log.getvalue()

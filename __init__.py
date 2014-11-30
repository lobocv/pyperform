__author__ = 'Calvin'
import inspect
import timeit
import StringIO
from types import FunctionType
from math import log10

__version__ = '1.1-beta'

def enable():
    """
    Enable all benchmarking.
    """
    Benchmark.enable = True
    ComparisonBenchmark.enable = True
    BenchmarkedFunction.enable = True
    BenchmarkedClass.enable = True


def disable():
    """
    Disable all benchmarking.
    """
    Benchmark.enable = False
    ComparisonBenchmark.enable = False
    BenchmarkedFunction.enable = False
    BenchmarkedClass.enable = False


def convert_time_units(t):
    """ Convert time in seconds into reasonable time units. """
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
    """ Strip the indentation level so the code runs in the global scope. """
    lines = src.splitlines()
    indent = len(lines[0]) - len(lines[0].strip(' '))
    func_src = ''
    for ii, l in enumerate(src.splitlines()):
        line = l[indent:]
        func_src += line + '\n'
    return func_src


def remove_decorators(src):
    """ Remove decorators from the source code """
    src_lines = src.splitlines()
    for n, line in enumerate(src_lines):
        if 'Benchmark' in line:
            del src_lines[n]
    setup_src = '\n'.join(src_lines)

    return setup_src


class Benchmark(object):
    timeit_repeat = 3
    timeit_number = 10000
    enable = True

    def __init__(self, setup=None, imports='', largs=None, kwargs=None):
        self.setup = setup
        self.imports = imports
        self.group = None
        self._is_bound_function = None
        if largs is not None and type(largs) is tuple:
            self._args = largs
        else:
            self._args = ()
        self._kwargs = kwargs.copy() if kwargs is not None else {}
        self.setup_src = ''
        self.callable = None
        self._is_function = None
        self.log = StringIO.StringIO()
        self.time_average_seconds = None

    def __call__(self, caller):
        if self.enable:
            self.callable = caller
            self._is_function = isinstance(caller, FunctionType)

            src = globalize_indentation(inspect.getsource(caller))
            src = remove_decorators(src)

            # Determine if the function is bound
            src_lines = src.splitlines()
            self._is_bound_function = 'def' in src_lines[0] and 'self' in src_lines[0]

            if callable(self.setup):
                setup_func = inspect.getsource(self.setup)
                setup_src = setup_func[setup_func.index('\n') + 1:]
                setup_src = globalize_indentation(setup_src)
                src = setup_src + '\n' + src
            else:
                src = src
            src += '\n'

            src = self.imports + '\n' + src
            self.setup_src = remove_decorators(src)
            self.log.write(self.setup_src)

            # Create the call statement
            if self._args and self._kwargs:
                self.stmt = "{0}(*{1}, **{2})".format(caller.__name__, self._args, self._kwargs)
            elif self._args:
                self.stmt = "{0}(*{1})".format(caller.__name__, self._args)
            elif self._kwargs:
                self.stmt = "{0}(**{1})".format(caller.__name__, self._kwargs)
            else:
                self.stmt = "{0}()".format(caller.__name__)

        return caller

    def write_log(self, fs=None):
        """
        Write the results of the benchmark to a log file.
        :param fs: file-like object.
        """
        log = StringIO.StringIO()
        log.write(self.setup_src)

        # If the function is not bound, write the test score to the log
        if not self._is_bound_function:
            time_avg = convert_time_units(self.time_average_seconds)
            log.write("\nAverage time: {0} \n".format(time_avg))

        if fs:
            with open(fs, 'w') as _f:
                _f.write(log.getvalue())

    def run_timeit(self, stmt, setup):
        """ Create the function call statement as a string used for timeit. """
        _timer = timeit.Timer(stmt=stmt, setup=setup)
        trials = _timer.repeat(self.timeit_repeat, self.timeit_number)
        self.time_average_seconds = sum(trials) / len(trials)
        # Convert into reasonable time units
        time_avg = convert_time_units(self.time_average_seconds)

        return time_avg


class BenchmarkedClass(Benchmark):
    bound_functions = {}

    def __init__(self, setup=None, cls_args=None, cls_kwargs=None, *args, **kwargs):
        super(BenchmarkedClass, self).__init__(setup, largs=cls_args, kwargs=cls_kwargs, *args, **kwargs)

    def __call__(self, cls):
        if self.enable:
            super(BenchmarkedClass, self).__call__(cls)
            setup_src = self.setup_src
            setup_src += '\ninstance = {}'.format(self.stmt)

            groups = set()
            for p in self.bound_functions[cls.__name__]:
                stmt = "instance.{}".format(p.stmt)
                p.run_timeit(stmt, setup_src)
                p.write_log()
                if p.group:
                    groups.add(p.group)

        return cls


class BenchmarkedFunction(Benchmark):
    def __call__(self, caller):
        if self.enable:
            super(BenchmarkedFunction, self).__call__(caller)
            self.run_timeit(self.stmt, self.setup_src)
            print "{} \t {}".format(caller.__name__, convert_time_units(self.time_average_seconds))
        return caller


class ComparisonBenchmark(Benchmark):
    groups = {}

    def __init__(self, group, classname=None, setup=None, *largs, **kwargs):
        super(ComparisonBenchmark, self).__init__(setup=setup, *largs, **kwargs)
        self.group = group
        self.classname = classname
        if group not in self.groups:
            self.groups[group] = []

    def __call__(self, caller):
        if self.enable:
            super(ComparisonBenchmark, self).__call__(caller)
            self.groups[self.group].append(self)
            # Bound functions are tested in ClassBenchmark.__call__
            # Just store a reference to the ComparisonBenchmark if the function is bound, otherwise, run the test
            if self._is_bound_function:
                try:
                    BenchmarkedClass.bound_functions[self.classname].append(self)
                except KeyError:
                    BenchmarkedClass.bound_functions[self.classname] = [self]
            else:
                # Run the test
                self.run_timeit(self.stmt, self.setup_src)

        return caller

    @staticmethod
    def summarize(group, fs=None):
        """
        Tabulate and write the results of ComparisonBenchmarks to a file or standard out.
        :param str group: name of the comparison group.
        :param fs: file-like object (Optional)
        """
        tests = sorted(ComparisonBenchmark.groups[group], key=lambda t: getattr(t, 'time_average_seconds'))
        log = StringIO.StringIO()

        fmt = "{0: <30} {1: <20} {2: <20}\n"
        log.write(fmt.format('Function Name', 'Time', 'Fraction of fastest'))
        log.write('{0:-<80} \n'.format(''))
        for t in tests:
            func_name = "{}.{}".format(t.classname, t.callable.__name__) if t.classname else t.callable.__name__
            log.write(fmt.format(func_name,
                                 convert_time_units(t.time_average_seconds),
                                 "{:.3f}".format(tests[0].time_average_seconds / t.time_average_seconds)))
        log.write('\n\nSource Code:\n')
        log.write('{0:-<80} \n'.format(''))
        for test in tests:
            log.write(test.log.getvalue())
            log.write('\n{0:-<80}\n'.format(''))

        if isinstance(fs, str):
            with open(fs, 'w') as f:
                f.write(log.getvalue())
        elif fs is None:
            print log.getvalue()
        else:
            try:
                fs.write(log.getvalue())
            except AttributeError as e:
                print e


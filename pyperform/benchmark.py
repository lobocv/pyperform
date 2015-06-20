__author__ = 'calvin'

import inspect
import timeit

from types import FunctionType
from .tools import *


class Benchmark(object):
    enable = True

    def __init__(self, setup=None, classname=None, timeit_repeat=3, timeit_number=1000, largs=None, kwargs=None):
        self.setup = setup
        self.timeit_repeat = timeit_repeat
        self.timeit_number = timeit_number
        self.classname = classname
        self.group = None
        self.is_class_method = None
        if largs is not None and type(largs) is tuple:
            self._args = largs[:]
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

            fp = inspect.getfile(caller)
            imports = get_tagged_imports(fp)
            func_src = remove_decorators(globalize_indentation(inspect.getsource(caller)))

            # Determine if the function is bound. If it is, keep track of it so we can run the benchmark after the class
            # benchmark has been initialized.
            src_lines = func_src.splitlines()
            self.is_class_method = 'def' in src_lines[0] and 'self' in src_lines[0]
            if self.is_class_method and self.classname:
                from .benchmarkedclass import BenchmarkedClass

                try:
                    BenchmarkedClass.bound_functions[self.classname].append(self)
                except KeyError:
                    BenchmarkedClass.bound_functions[self.classname] = [self]

            if callable(self.setup):
                setup_func = inspect.getsource(self.setup)
                setup_src = globalize_indentation(setup_func[setup_func.index('\n') + 1:])
            elif type(self.setup) == str:
                setup_src = self.setup
            else:
                setup_src = ''

            src = '\n'.join([imports, setup_src, func_src])
            self.setup_src = src + '\n'
            self.log.write(self.setup_src)

            self.stmt = generate_call_statement(caller, self.is_class_method, *self._args, **self._kwargs)

        return caller

    def write_log(self, fs=None):
        """
        Write the results of the benchmark to a log file.
        :param fs: file-like object.
        """
        log = StringIO.StringIO()
        log.write(self.setup_src)

        # If the function is not bound, write the test score to the log
        if not self.is_class_method:
            time_avg = convert_time_units(self.time_average_seconds)
            log.write("\nAverage time: {0} \n".format(time_avg))

        if fs:
            with open(fs, 'w') as _f:
                _f.write(log.getvalue())

    def run_timeit(self, stmt, setup):
        """ Create the function call statement as a string used for timeit. """
        _timer = timeit.Timer(stmt=stmt, setup=setup)
        trials = _timer.repeat(self.timeit_repeat, self.timeit_number)
        self.time_average_seconds = sum(trials) / len(trials) / self.timeit_number
        # Convert into reasonable time units
        time_avg = convert_time_units(self.time_average_seconds)
        return time_avg

from __future__ import print_function

import inspect
import timeit
import sys

import logging
from types import FunctionType
from math import log10

if sys.version[0] == '3':
    import io as StringIO
else:
    import StringIO
__version__ = '1.4'
logging.getLogger().setLevel(logging.INFO)


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
    src = src.strip()
    src_lines = src.splitlines()
    for n, line in enumerate(src_lines):
        if 'Benchmark' in line:
            del src_lines[n]
    setup_src = '\n'.join(src_lines)

    return setup_src


class Benchmark(object):
    enable = True

    def __init__(self, setup=None, imports='', timeit_repeat=3, timeit_number=1000, largs=None, kwargs=None):
        self.setup = setup
        self.imports = imports
        self.timeit_repeat = timeit_repeat
        self.timeit_number = timeit_number
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
            self.setup_src = remove_decorators(src) + '\n'
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
        self.time_average_seconds = sum(trials) / len(trials) / self.timeit_number
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
                stmt = p.stmt
                p.run_timeit(stmt, setup_src)
                p.write_log()
                if p.result_validation and p.group not in groups:
                    self.validate(p.groups[p.group])
                groups.add(p.group)

        return cls


    def validate(self, benchmarks):
        # Execute the code once to get it's results (to be used in function validation)
        class_code = self.setup_src
        instance_creation = '\ninstance = {}'.format(self.stmt)
        for i, benchmark in enumerate(benchmarks):
            if not benchmark.result_validation:
                break

            validation_code = class_code + instance_creation + '\nvalidation_result = ' + benchmark.stmt
            validation_scope = {}
            exec (validation_code, validation_scope)
            # Store the result in the first function in the group.
            if i == 0:
                compare_against_function = benchmarks[0].callable.__name__
                compare_against_result = validation_scope['validation_result']
            else:
                if compare_against_result == validation_scope['validation_result']:
                    logging.info('Validating {} against {}......PASSED!'.format(benchmark.callable.__name__,
                                                                                compare_against_function))
                else:
                    error = 'Results of functions {0} and {1} are not equivalent.\n{0}:\t {2}\n{1}:\t{3}'
                    logging.info(error.format(compare_against_function, benchmark.callable.__name__,
                                              compare_against_result, validation_scope['validation_result']))


class BenchmarkedFunction(Benchmark):
    def __call__(self, caller):
        if self.enable:
            super(BenchmarkedFunction, self).__call__(caller)
            self.run_timeit(self.stmt, self.setup_src)
            print("{} \t {}".format(caller.__name__, convert_time_units(self.time_average_seconds)))
        return caller


class ComparisonBenchmark(Benchmark):
    groups = {}

    def __init__(self, group, classname=None, setup=None, validation=False, *largs, **kwargs):
        super(ComparisonBenchmark, self).__init__(setup=setup, *largs, **kwargs)
        self.group = group
        self.classname = classname
        self.result_validation = validation
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
                self.stmt = 'instance.' + self.stmt
            else:
                # Run the test
                self.run_timeit(self.stmt, self.setup_src)

                if self.result_validation:
                    self.validate()

        return caller

    def validate(self):
        # Execute the code once to get it's results (to be used in function validation)
        validation_code = self.setup_src + '\nvalidation_result = ' + self.stmt
        validation_scope = {}
        exec (validation_code, validation_scope)
        # Store the result in the first function in the group.
        if len(self.groups[self.group]) == 1:
            self.result = validation_scope['validation_result']
        else:
            compare_against = self.groups[self.group][0]
            test = [benchmark.result_validation for benchmark in self.groups[self.group]]
            if not all(test):
                raise ValueError('All functions within a group must have the same validation flag.')
            compare_result = compare_against.result
            if compare_result == validation_scope['validation_result']:
                logging.info('Validating {}......PASSED!'.format(benchmark.callable.__name__))
            else:
                error = 'Results of functions {0} and {1} are not equivalent.\n{0}:\t {2}\n{1}:\t{3}'
                logging.info(error.format(compare_against.callable.__name__, self.callable.__name__,
                                          compare_result, validation_scope['validation_result']))


    @staticmethod
    def summarize(group, fs=None):
        """
        Tabulate and write the results of ComparisonBenchmarks to a file or standard out.
        :param str group: name of the comparison group.
        :param fs: file-like object (Optional)
        """
        _line_break = '{0:-<100}'.format('')
        tests = sorted(ComparisonBenchmark.groups[group], key=lambda t: getattr(t, 'time_average_seconds'))
        log = StringIO.StringIO()
        log.write('List Arguments: {}\n'.format(*tests[0]._args))
        kwargs = ["{} = {}".format(k, v) for k, v in tests[0]._kwargs.iteritems()]
        log.write('Keyword Arguments: %s' % ','.join(kwargs))
        log.write('\n\n\n')
        fmt = "{0: <35} {1: <12} {2: <15} {3: <15} {4: <14}\n"
        log.write(fmt.format('Function Name', 'Time', '% of Fastest', 'timeit_repeat', 'timeit_number'))
        log.write(_line_break)
        log.write('\n')



        for t in tests:
            func_name = "{}.{}".format(t.classname, t.callable.__name__) if t.classname else t.callable.__name__
            log.write(fmt.format(func_name,
                                 convert_time_units(t.time_average_seconds),
                                 "{:.1f}".format(tests[0].time_average_seconds / t.time_average_seconds * 100),
                                 t.timeit_repeat,
                                 t.timeit_number))
        log.write(_line_break)

        log.write('\n\n\nSource Code:\n')
        log.write(_line_break)
        log.write('\n')
        for test in tests:
            log.write(test.log.getvalue())
            log.write('\n')

        if isinstance(fs, str):
            with open(fs, 'w') as f:
                f.write(log.getvalue())
        elif fs is None:
            print(log.getvalue())
        else:
            try:
                fs.write(log.getvalue())
            except AttributeError as e:
                print(e)


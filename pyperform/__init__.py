from __future__ import print_function

import logging
import inspect
import timeit
import time
import sys

from types import FunctionType
from math import log10

if sys.version[0] == '3':
    import io as StringIO               # Python 3.x
else:
    import cStringIO as StringIO        # Python 2.x
    range = xrange

__version__ = '1.72'
_import_tag = '#!'


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


def set_import_tag(tag):
    if type(tag) == str:
        globals()['_import_tag'] = tag


def convert_time_units(t):
    """ Convert time in seconds into reasonable time units. """
    order = log10(t)
    if -9 < order < -6:
        time_units = 'ns'
        factor = 1000000000
    elif -6 < order < -3:
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
    multi_line = False
    n_deleted = 0
    for n in range(len(src_lines)):
        line = src_lines[n - n_deleted].strip()
        if (line.startswith('@') and 'Benchmark' in line) or multi_line:
            del src_lines[n - n_deleted]
            n_deleted += 1
            if line.endswith(')'):
                multi_line = False
            else:
                multi_line = True
    setup_src = '\n'.join(src_lines)
    return setup_src


def get_tagged_imports(fp, tag):
    with open(fp, 'r') as f:
        imports = [l[:l.index(tag)] for l in f if tag in l and (l.startswith('import') or l.startswith('from'))]
    src = '\n'.join(imports)
    return src


def generate_call_statement(func, is_class_method, *args, **kwargs):
    # Create the call statement
    if is_class_method:
        stmt = 'instance.' + func.__name__ + '('
    else:
        stmt = func.__name__ + '('
    for arg in args:
        stmt += arg.__repr__() + ', '
    for kw, val in kwargs.items():
        stmt += '{0}={1}, '.format(kw, val.__repr__())
    stmt = stmt.strip(', ')
    stmt += ')'
    return stmt


class ValidationError(Exception):
    pass


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
            imports = get_tagged_imports(fp, _import_tag)
            func_src = remove_decorators(globalize_indentation(inspect.getsource(caller)))

            # Determine if the function is bound. If it is, keep track of it so we can run the benchmark after the class
            # benchmark has been initialized.
            src_lines = func_src.splitlines()
            self.is_class_method = 'def' in src_lines[0] and 'self' in src_lines[0]
            if self.is_class_method and self.classname:
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


class BenchmarkedClass(Benchmark):
    bound_functions = {}

    def __init__(self, setup=None, largs=None, kwargs=None, **kw):
        super(BenchmarkedClass, self).__init__(setup, largs=largs, kwargs=kwargs, **kw)

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
                if isinstance(p, BenchmarkedFunction):
                    print("{} \t {}".format(p.callable.__name__, convert_time_units(p.time_average_seconds)))
                if hasattr(p, 'result_validation') and p.result_validation and p.group not in groups:
                    self.validate(p.groups[p.group])
                groups.add(p.group)

        return cls


    def validate(self, benchmarks):
        """
        Execute the code once to get it's results (to be used in function validation). Compare the result to the
        first function in the group.
        :param benchmarks: list of benchmarks to validate.
        """
        class_code = self.setup_src
        instance_creation = '\ninstance = {}'.format(self.stmt)
        for i, benchmark in enumerate(benchmarks):
            if not benchmark.result_validation:
                break

            validation_code = class_code + instance_creation + '\nvalidation_result = ' + benchmark.stmt
            validation_scope = {}
            exec(validation_code, validation_scope)
            # Store the result in the first function in the group.
            if i == 0:
                compare_against_function = benchmarks[0].callable.__name__
                compare_against_result = validation_scope['validation_result']
                logging.info('PyPerform: Validating group "{b.group}" against method '
                             '"{b.classname}.{b.callable.__name__}"'.format(b=benchmarks[0]))
            else:
                if compare_against_result == validation_scope['validation_result']:
                    logging.info('PyPerform: Validating {b.classname}.{b.callable.__name__}......PASSED!'
                                 .format(b=benchmark))
                else:
                    error = 'Results of functions {0} and {1} are not equivalent.\n{0}:\t {2}\n{1}:\t{3}'
                    raise ValidationError(error.format(compare_against_function, benchmark.callable.__name__,
                                              compare_against_result, validation_scope['validation_result']))


class BenchmarkedFunction(Benchmark):
    def __call__(self, caller):
        if self.enable:
            super(BenchmarkedFunction, self).__call__(caller)
            if not self.is_class_method:
                self.run_timeit(self.stmt, self.setup_src)
                print("{} \t {}".format(caller.__name__, convert_time_units(self.time_average_seconds)))
        return caller


class ComparisonBenchmark(Benchmark):
    groups = {}

    def __init__(self, group, classname=None, setup=None, validation=False, largs=None, kwargs=None, **kw):
        super(ComparisonBenchmark, self).__init__(setup=setup, largs=largs, kwargs=kwargs, **kw)
        self.group = group
        self.classname = classname
        self.result_validation = validation
        self.result = None
        if group not in self.groups:
            self.groups[group] = []

    def __call__(self, caller):
        if self.enable:
            super(ComparisonBenchmark, self).__call__(caller)
            self.groups[self.group].append(self)
            # Bound functions are tested in ClassBenchmark.__call__
            # Just store a reference to the ComparisonBenchmark if the function is bound, otherwise, run the test
            if not self.is_class_method:
                # Run the test
                self.run_timeit(self.stmt, self.setup_src)
                if self.result_validation:
                    self.validate()
        return caller

    def validate(self):
        """
        Execute the code once to get it's results (to be used in function validation). Compare the result to the
        first function in the group.
        """
        validation_code = self.setup_src + '\nvalidation_result = ' + self.stmt
        validation_scope = {}
        exec(validation_code, validation_scope)
        # Store the result in the first function in the group.
        if len(self.groups[self.group]) == 1:
            self.result = validation_scope['validation_result']
            logging.info('PyPerform: Validating group "{b.group}" against function "{b.callable.__name__}"'
                         .format(b=self))
        else:
            compare_against_benchmark = self.groups[self.group][0]
            test = [benchmark.result_validation for benchmark in self.groups[self.group]]
            if not all(test):
                raise ValueError('All functions within a group must have the same validation flag.')
            compare_result = compare_against_benchmark.result
            if compare_result == validation_scope['validation_result']:
                logging.info('PyPerform: Validating {}......PASSED!'.format(self.callable.__name__))
            else:
                error = 'Results of functions {0} and {1} are not equivalent.\n{0}:\t {2}\n{1}:\t{3}'
                raise ValidationError(error.format(compare_against_benchmark.callable.__name__, self.callable.__name__,
                                          compare_result, validation_scope['validation_result']))


    @staticmethod
    def summarize(group, fs=None, include_source=True):
        """
        Tabulate and write the results of ComparisonBenchmarks to a file or standard out.
        :param str group: name of the comparison group.
        :param fs: file-like object (Optional)
        """
        _line_break = '{0:-<120}\n'.format('')
        tests = sorted(ComparisonBenchmark.groups[group], key=lambda t: getattr(t, 'time_average_seconds'))
        log = StringIO.StringIO()
        log.write('Call statement:\n\n')
        log.write('\t' + tests[0].stmt)
        log.write('\n\n\n')
        fmt = "{0: <8} {1: <35} {2: <12} {3: <15} {4: <15} {5: <14}\n"
        log.write(fmt.format('Rank', 'Function Name', 'Time', '% of Fastest', 'timeit_repeat', 'timeit_number'))
        log.write(_line_break)
        log.write('\n')

        for i, t in enumerate(tests):
            func_name = "{}.{}".format(t.classname, t.callable.__name__) if t.classname else t.callable.__name__
            log.write(fmt.format(i+1,
                                 func_name,
                                 convert_time_units(t.time_average_seconds),
                                 "{:.1f}".format(tests[0].time_average_seconds / t.time_average_seconds * 100),
                                 t.timeit_repeat,
                                 t.timeit_number))
        log.write(_line_break)

        if include_source:
            log.write('\n\n\nSource Code:\n')
            log.write(_line_break)
            for test in tests:
                log.write(test.log.getvalue())
                log.write(_line_break)

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


def timer(func):
    def _timed_function(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        print(func.__name__, ':\t', convert_time_units(t2-t1))
        return result

    _timed_function.__name__ = "_timed_{}".format(func.__name__)
    return _timed_function

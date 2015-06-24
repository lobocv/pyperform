__author__ = 'calvin'

import logging

from .benchmark import Benchmark
from .tools import *
from .exceptions import ValidationError


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
        log.write(fmt.format('Rank', 'Function Name', 'Time', '% of Slowest', 'timeit_repeat', 'timeit_number'))
        log.write(_line_break)
        log.write('\n')

        for i, t in enumerate(tests):
            func_name = "{}.{}".format(t.classname, t.callable.__name__) if t.classname else t.callable.__name__
            if i == len(tests)-1:
                time_percent = 'Slowest'
            else:
                time_percent = "{:.1f}".format(t.time_average_seconds / tests[-1].time_average_seconds * 100)
            log.write(fmt.format(i+1,
                                 func_name,
                                 convert_time_units(t.time_average_seconds),
                                 time_percent,
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

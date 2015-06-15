__author__ = 'calvin'

import logging
from .benchmark import Benchmark
from .benchmarkedfunction import BenchmarkedFunction
from .tools import convert_time_units
from .exceptions import ValidationError


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

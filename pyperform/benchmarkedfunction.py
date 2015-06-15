__author__ = 'calvin'

from .benchmark import Benchmark
from .tools import convert_time_units

class BenchmarkedFunction(Benchmark):

    def __call__(self, caller):
        if self.enable:
            super(BenchmarkedFunction, self).__call__(caller)
            if not self.is_class_method:
                self.run_timeit(self.stmt, self.setup_src)
                print("{} \t {}".format(caller.__name__, convert_time_units(self.time_average_seconds)))
        return caller

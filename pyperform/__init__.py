from __future__ import print_function

__version__ = '1.73'


from pyperform.benchmark import Benchmark
from .comparisonbenchmark import ComparisonBenchmark
from .benchmarkedclass import BenchmarkedClass
from .benchmarkedfunction import BenchmarkedFunction
from .timer import timer
from .exceptions import ValidationError


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












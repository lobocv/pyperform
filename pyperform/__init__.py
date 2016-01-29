from __future__ import print_function

__version__ = '1.86'
import sys

if sys.version[0] == '3':
    import io as StringIO  # Python 3.x
else:
    import cStringIO as StringIO  # Python 2.x

    range = xrange

from pyperform.benchmark import Benchmark
from .comparisonbenchmark import ComparisonBenchmark
from .benchmarkedclass import BenchmarkedClass
from .benchmarkedfunction import BenchmarkedFunction
from .thread import Thread
from .timer import timer
from .exceptions import ValidationError
from .customlogger import CustomLogLevel, new_log_level


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












__author__ = 'calvin'
"""
This example demonstrates the performance benefit of using list comprehension instead of for loop and append.
It also demonstrates how to use imported modules in your benchmarks as well as compare functions of the same group.
"""

try:
    from builtins import range
except ImportError:
    range = xrange
from math import sin  #!

from pyperform import ComparisonBenchmark


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_append(n, *args, **kwargs):
    l = []
    for i in range(1, n):
        l.append(sin(i))
    return l


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_comprehension(n, *args, **kwargs):
    l = [sin(i) for i in range(1, n)]
    return l


ComparisonBenchmark.summarize('Group1', fs='report.txt')

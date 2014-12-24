__author__ = 'calvin'
"""
This example demonstrates the performance benefit of using list comprehension instead of for loop and append.
It also demonstrates how to use imported modules in your benchmarks as well as compare functions of the same group.
"""

from pyperform import ComparisonBenchmark
from math import sin  #!


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_append(n, *args, **kwargs):
    l = []
    for i in xrange(1, n):
        l.append(sin(i))
    return l


@ComparisonBenchmark('Group1', validation=True, largs=(100,))
def list_comprehension(n, *args, **kwargs):
    l = [sin(i) for i in xrange(1, n)]
    return l


ComparisonBenchmark.summarize('Group1', fs='report.txt')
